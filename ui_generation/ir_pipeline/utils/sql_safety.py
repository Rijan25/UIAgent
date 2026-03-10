from __future__ import annotations

import re
import sqlite3
from pathlib import Path
from typing import Any, Dict, Iterable, List, Set

from .db_snapshot import extract_allowlists


class SQLValidationError(ValueError):
    pass


_FORBIDDEN_KEYWORDS = {
    "insert",
    "update",
    "delete",
    "drop",
    "alter",
    "create",
    "replace",
    "truncate",
    "attach",
    "detach",
    "pragma",
    "vacuum",
    "reindex",
    "analyze",
    "begin",
    "commit",
    "rollback",
}

_SAFE_FUNCTIONS = {
    "count",
    "sum",
    "avg",
    "min",
    "max",
    "lower",
    "upper",
    "coalesce",
    "ifnull",
    "nullif",
    "substr",
    "length",
    "round",
    "abs",
    "trim",
    "ltrim",
    "rtrim",
    "date",
    "datetime",
    "strftime",
    "cast",
}

_SQL_KEYWORDS = {
    "select",
    "from",
    "where",
    "and",
    "or",
    "not",
    "null",
    "is",
    "like",
    "in",
    "between",
    "order",
    "by",
    "group",
    "having",
    "limit",
    "offset",
    "asc",
    "desc",
    "join",
    "inner",
    "left",
    "right",
    "full",
    "on",
    "as",
    "with",
    "distinct",
    "case",
    "when",
    "then",
    "else",
    "end",
    "union",
    "all",
    "exists",
}

_IDENT = r"[A-Za-z_][A-Za-z0-9_]*"
_PLACEHOLDER_RE = re.compile(r":([A-Za-z_][A-Za-z0-9_]*)")


def _strip_comments(sql: str) -> str:
    without_line = re.sub(r"--[^\n]*", "", sql)
    without_block = re.sub(r"/\*.*?\*/", "", without_line, flags=re.DOTALL)
    return without_block


def _normalize_sql(sql: str) -> str:
    cleaned = _strip_comments(sql).strip()
    if not cleaned:
        raise SQLValidationError("SQL query is empty.")
    cleaned = cleaned.rstrip(";").strip()
    return cleaned


def _ensure_single_statement(sql: str) -> None:
    if ";" in sql:
        raise SQLValidationError("SQL must contain exactly one statement.")


def _ensure_select_only(sql: str) -> None:
    lowered = sql.lower()
    if not (lowered.startswith("select") or lowered.startswith("with")):
        raise SQLValidationError("Only SELECT/CTE SELECT queries are allowed.")

    for keyword in _FORBIDDEN_KEYWORDS:
        if re.search(rf"\b{keyword}\b", lowered):
            raise SQLValidationError(f"Forbidden SQL keyword detected: {keyword}")

    if re.search(r"\bload_extension\s*\(", lowered):
        raise SQLValidationError("Unsafe SQL function detected: load_extension")


def _extract_aliases(sql: str) -> Set[str]:
    aliases = set()
    for match in re.finditer(rf"\bas\s+({_IDENT})\b", sql, flags=re.IGNORECASE):
        aliases.add(match.group(1).lower())
    return aliases


def _extract_table_refs(sql: str) -> Set[str]:
    refs = set()
    for match in re.finditer(rf"\b(?:from|join)\s+({_IDENT})\b", sql, flags=re.IGNORECASE):
        refs.add(match.group(1))
    if not refs:
        raise SQLValidationError("SQL query must include at least one FROM table.")
    return refs


def _extract_alias_to_table(sql: str) -> Dict[str, str]:
    alias_map: Dict[str, str] = {}
    for match in re.finditer(
        rf"\b(?:from|join)\s+({_IDENT})\s+(?:as\s+)?({_IDENT})\b",
        sql,
        flags=re.IGNORECASE,
    ):
        table_name = match.group(1)
        alias = match.group(2)
        if alias.lower() in _SQL_KEYWORDS:
            continue
        alias_map[alias] = table_name
    return alias_map


def _extract_select_clause(sql: str) -> str:
    match = re.search(r"\bselect\b(.*?)\bfrom\b", sql, flags=re.IGNORECASE | re.DOTALL)
    if not match:
        raise SQLValidationError("Unable to parse SELECT clause.")
    return match.group(1)


def _split_top_level_csv(segment: str) -> List[str]:
    parts: List[str] = []
    current: List[str] = []
    depth = 0
    in_single = False
    in_double = False
    for ch in segment:
        if ch == "'" and not in_double:
            in_single = not in_single
        elif ch == '"' and not in_single:
            in_double = not in_double
        elif not in_single and not in_double:
            if ch == "(":
                depth += 1
            elif ch == ")" and depth > 0:
                depth -= 1
            elif ch == "," and depth == 0:
                parts.append("".join(current).strip())
                current = []
                continue
        current.append(ch)
    if current:
        parts.append("".join(current).strip())
    return [p for p in parts if p]


def _strip_literals(sql: str) -> str:
    sql = re.sub(r"'(?:''|[^'])*'", "''", sql)
    sql = re.sub(r'"(?:""|[^"])*"', '""', sql)
    return sql


def _extract_identifier_tokens(sql: str) -> Set[str]:
    raw = _strip_literals(sql)
    return {match.group(0) for match in re.finditer(_IDENT, raw)}


def _validate_tables_and_columns(sql: str, snapshot: Dict[str, Any]) -> None:
    allow = extract_allowlists(snapshot)
    allowed_tables: Set[str] = set(allow["tables"])
    columns_by_table: Dict[str, Set[str]] = dict(allow["columns_by_table"])
    allowed_table_lookup = {table.lower(): table for table in allowed_tables}
    columns_by_table_lower = {
        table: {column.lower() for column in columns}
        for table, columns in columns_by_table.items()
    }

    raw_table_refs = _extract_table_refs(sql)
    table_refs: Set[str] = set()
    unknown_tables: List[str] = []
    for table in raw_table_refs:
        canonical = allowed_table_lookup.get(table.lower())
        if canonical is None:
            unknown_tables.append(table)
            continue
        table_refs.add(canonical)

    raw_alias_to_table = _extract_alias_to_table(sql)
    alias_to_table: Dict[str, str] = {}
    for alias, table in raw_alias_to_table.items():
        canonical = allowed_table_lookup.get(table.lower())
        if canonical is not None:
            alias_to_table[alias] = canonical

    table_ref_lower = {t.lower() for t in table_refs}
    alias_lower = {a.lower() for a in alias_to_table}
    if unknown_tables:
        raise SQLValidationError(f"Unknown table reference(s): {', '.join(sorted(unknown_tables))}")

    selected = _extract_select_clause(sql)
    selections = _split_top_level_csv(selected)
    for expr in selections:
        if expr == "*":
            continue
        star_match = re.match(rf"^\s*({_IDENT})\.\*\s*$", expr)
        if star_match:
            table_name = star_match.group(1)
            table_name = alias_to_table.get(table_name, table_name)
            if table_name not in table_refs:
                raise SQLValidationError(f"Unknown table in wildcard selection: {table_name}")
            continue

        for table_name, column_name in re.findall(rf"\b({_IDENT})\.({_IDENT})\b", expr):
            table_name = alias_to_table.get(table_name, table_name)
            if table_name not in table_refs:
                raise SQLValidationError(f"Unknown table reference in SELECT: {table_name}")
            if column_name.lower() not in columns_by_table_lower.get(table_name, set()):
                raise SQLValidationError(f"Unknown column reference in SELECT: {table_name}.{column_name}")

        tokens = _extract_identifier_tokens(expr)
        aliases = _extract_aliases(expr)
        for token in tokens:
            token_l = token.lower()
            if token_l in _SQL_KEYWORDS:
                continue
            if token_l in aliases:
                continue
            if token_l in table_ref_lower:
                continue
            if token_l in alias_lower:
                continue
            if token_l in _SAFE_FUNCTIONS:
                continue
            # Ignore clearly typed aliases (e.g., CAST(x AS INTEGER))
            if token_l in {"integer", "real", "text", "numeric"}:
                continue
            if "." in token_l:
                continue
            if not any(token_l in columns for columns in columns_by_table_lower.values()):
                raise SQLValidationError(f"Unknown identifier in SELECT clause: {token}")


def _normalize_pagination(sql: str, max_limit: int) -> str:
    normalized = sql
    lower = normalized.lower()

    literal_limit_match = re.search(r"\blimit\s+(\d+)\b", lower)
    if literal_limit_match:
        literal_limit = int(literal_limit_match.group(1))
        if literal_limit > max_limit:
            raise SQLValidationError(
                f"Literal LIMIT {literal_limit} exceeds max_page_size {max_limit}. Use :limit placeholder."
            )

    if not re.search(r"\blimit\b", lower):
        normalized = f"{normalized} LIMIT :limit OFFSET :offset"
        return normalized

    if re.search(r"\blimit\s*:\s*limit\b", lower):
        if not re.search(r"\boffset\s*:\s*offset\b", lower):
            normalized = f"{normalized} OFFSET :offset"
        return normalized

    if re.search(r"\blimit\s+\d+\b", lower):
        # Convert literal pagination to placeholders so runtime can page safely.
        normalized = re.sub(
            r"\blimit\s+\d+\s*(?:offset\s+\d+)?\s*$",
            "LIMIT :limit OFFSET :offset",
            normalized,
            flags=re.IGNORECASE,
        )
        if re.search(r"\blimit\s*:\s*limit\b", normalized.lower()):
            return normalized

    raise SQLValidationError("Query must use LIMIT :limit and OFFSET :offset placeholders.")


def _extract_placeholders(sql: str) -> Set[str]:
    return {f":{match.group(1)}" for match in _PLACEHOLDER_RE.finditer(sql)}


def _normalize_allowed_params(params: Iterable[str] | None) -> Set[str]:
    if params is None:
        return {":limit", ":offset", ":search"}
    normalized: Set[str] = set()
    for raw in params:
        if not isinstance(raw, str):
            continue
        stripped = raw.strip()
        if not stripped:
            continue
        normalized.add(stripped if stripped.startswith(":") else f":{stripped}")
    if not normalized:
        normalized = {":limit", ":offset", ":search"}
    return normalized


def _validate_params(sql: str, allowed_params: Set[str]) -> Set[str]:
    placeholders = _extract_placeholders(sql)
    required = {":limit", ":offset"}
    missing = [param for param in sorted(required) if param not in placeholders]
    if missing:
        raise SQLValidationError(f"Missing required pagination parameter(s): {', '.join(missing)}")

    disallowed = [name for name in sorted(placeholders) if name not in allowed_params]
    if disallowed:
        raise SQLValidationError(
            f"Disallowed SQL parameter(s): {', '.join(disallowed)}. Allowed: {', '.join(sorted(allowed_params))}"
        )
    return placeholders


def validate_and_normalize_sql_template(
    sql_template: str,
    snapshot: Dict[str, Any],
    max_limit: int,
    allowed_params: Iterable[str] | None = None,
) -> Dict[str, Any]:
    if max_limit <= 0:
        raise SQLValidationError("max_page_size must be positive.")

    normalized = _normalize_sql(sql_template)
    _ensure_single_statement(normalized)
    _ensure_select_only(normalized)
    _validate_tables_and_columns(normalized, snapshot=snapshot)
    normalized = _normalize_pagination(normalized, max_limit=max_limit)

    allowed = _normalize_allowed_params(allowed_params)
    placeholders = _validate_params(normalized, allowed_params=allowed)

    return {
        "sql_template": normalized,
        "params": sorted(placeholders),
    }


def _bind_for_explain(placeholders: Set[str], max_limit: int) -> Dict[str, Any]:
    values: Dict[str, Any] = {}
    for placeholder in placeholders:
        key = placeholder[1:]
        if key == "limit":
            values[key] = min(1, max_limit)
        elif key == "offset":
            values[key] = 0
        elif key == "search":
            values[key] = ""
        else:
            values[key] = 0
    return values


def validate_sql_execution(
    sql_template: str,
    db_path: Path,
    max_limit: int,
    params: Iterable[str] | None = None,
) -> None:
    if not db_path.exists():
        raise SQLValidationError(f"SQLite DB not found for SQL execution check: {db_path}")

    placeholders = _extract_placeholders(sql_template)
    allowed = _normalize_allowed_params(params)
    _validate_params(sql_template, allowed_params=allowed)
    bindings = _bind_for_explain(placeholders=placeholders, max_limit=max_limit)

    try:
        with sqlite3.connect(str(db_path)) as conn:
            conn.execute(f"EXPLAIN QUERY PLAN {sql_template}", bindings).fetchall()
            conn.execute(sql_template, bindings).fetchmany(1)
    except sqlite3.Error as exc:
        raise SQLValidationError(f"SQL execution validation failed: {exc}") from exc
