from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from shutil import copy2
from typing import Any, Dict, List


def _quoted_ident(name: str) -> str:
    return '"' + name.replace('"', '""') + '"'


def _fetch_table_names(conn: sqlite3.Connection) -> List[str]:
    rows = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name"
    ).fetchall()
    return [row[0] for row in rows]


def _fetch_columns(conn: sqlite3.Connection, table: str) -> List[Dict[str, Any]]:
    pragma = conn.execute(f"PRAGMA table_info({_quoted_ident(table)})").fetchall()
    return [
        {
            "name": row[1],
            "type": row[2],
            "not_null": bool(row[3]),
            "default": row[4],
            "pk": bool(row[5]),
        }
        for row in pragma
    ]


def _fetch_foreign_keys(conn: sqlite3.Connection, table: str) -> List[Dict[str, Any]]:
    pragma = conn.execute(f"PRAGMA foreign_key_list({_quoted_ident(table)})").fetchall()
    return [
        {
            "from_column": row[3],
            "to_table": row[2],
            "to_column": row[4],
            "on_update": row[5],
            "on_delete": row[6],
        }
        for row in pragma
    ]


def _fetch_sample_rows(conn: sqlite3.Connection, table: str, limit: int) -> List[Dict[str, Any]]:
    cursor = conn.execute(f"SELECT * FROM {_quoted_ident(table)} LIMIT ?", (limit,))
    columns = [d[0] for d in cursor.description or []]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]


def _fetch_row_count(conn: sqlite3.Connection, table: str) -> int:
    row = conn.execute(f"SELECT COUNT(*) FROM {_quoted_ident(table)}").fetchone()
    return int(row[0]) if row else 0


def generate_external_db_snapshot(
    db_path: Path,
    snapshot_path: Path,
    source_id: str = "student_external",
    sample_rows_per_table: int = 10,
) -> Dict[str, Any]:
    if not db_path.exists():
        raise FileNotFoundError(f"SQLite DB not found: {db_path}")

    with sqlite3.connect(str(db_path)) as conn:
        conn.row_factory = sqlite3.Row
        table_names = _fetch_table_names(conn)

        tables: Dict[str, Any] = {}
        relationships: List[Dict[str, str]] = []
        for table in table_names:
            columns = _fetch_columns(conn, table)
            foreign_keys = _fetch_foreign_keys(conn, table)
            primary_key = [column["name"] for column in columns if column["pk"]]

            for fk in foreign_keys:
                relationships.append(
                    {
                        "from_table": table,
                        "from_column": str(fk["from_column"]),
                        "to_table": str(fk["to_table"]),
                        "to_column": str(fk["to_column"]),
                    }
                )

            tables[table] = {
                "schema": {
                    "columns": columns,
                    "primary_key": primary_key,
                    "foreign_keys": foreign_keys,
                },
                "row_count": _fetch_row_count(conn, table),
                "sample_rows": _fetch_sample_rows(conn, table, max(1, sample_rows_per_table)),
            }

    snapshot: Dict[str, Any] = {
        "source": {
            "source_id": source_id,
            "kind": "sqlite_snapshot",
            "origin_db_path": str(db_path),
            "generated_at": datetime.now(tz=timezone.utc).isoformat(),
        },
        "tables": tables,
        "relationships": relationships,
    }

    snapshot_path.parent.mkdir(parents=True, exist_ok=True)
    snapshot_path.write_text(json.dumps(snapshot, indent=2) + "\n", encoding="utf-8")
    return snapshot


def load_external_db_snapshot(snapshot_path: Path) -> Dict[str, Any]:
    return json.loads(snapshot_path.read_text(encoding="utf-8"))


def ensure_external_db_snapshot(
    db_path: Path,
    snapshot_path: Path,
    source_id: str = "student_external",
    sample_rows_per_table: int = 10,
) -> Dict[str, Any]:
    return generate_external_db_snapshot(
        db_path=db_path,
        snapshot_path=snapshot_path,
        source_id=source_id,
        sample_rows_per_table=sample_rows_per_table,
    )


def build_schema_prompt_context(
    snapshot: Dict[str, Any],
    include_samples: bool = False,
) -> str:
    source = snapshot.get("source", {})
    tables = snapshot.get("tables", {})
    relationships = snapshot.get("relationships", [])

    prompt_payload: Dict[str, Any] = {
        "source": {
            "source_id": source.get("source_id"),
            "kind": source.get("kind"),
            "generated_at": source.get("generated_at"),
        },
        "tables": {},
        "relationships": relationships,
    }

    for table_name, table_data in tables.items():
        schema = table_data.get("schema", {})
        table_payload: Dict[str, Any] = {
            "row_count": table_data.get("row_count", 0),
            "columns": schema.get("columns", []),
            "primary_key": schema.get("primary_key", []),
            "foreign_keys": schema.get("foreign_keys", []),
        }
        if include_samples:
            table_payload["sample_rows"] = table_data.get("sample_rows", [])
        prompt_payload["tables"][table_name] = table_payload

    return json.dumps(prompt_payload, indent=2)


def extract_allowlists(snapshot: Dict[str, Any]) -> Dict[str, Any]:
    tables = snapshot.get("tables", {})
    columns_by_table: Dict[str, set[str]] = {}
    for table_name, table_data in tables.items():
        schema = table_data.get("schema", {})
        columns = schema.get("columns", [])
        columns_by_table[table_name] = {
            str(column.get("name"))
            for column in columns
            if isinstance(column, dict) and isinstance(column.get("name"), str)
        }
    return {
        "tables": set(tables.keys()),
        "columns_by_table": columns_by_table,
    }


def sync_frontend_db_asset(
    db_path: Path,
    frontend_public_db_dir: Path,
) -> Path:
    frontend_public_db_dir.mkdir(parents=True, exist_ok=True)
    destination = frontend_public_db_dir / db_path.name
    copy2(db_path, destination)
    return destination


def sync_frontend_sql_wasm_asset(frontend_root: Path) -> Path | None:
    source = frontend_root / "node_modules" / "sql.js" / "dist" / "sql-wasm.wasm"
    if not source.exists():
        return None
    destination_dir = frontend_root / "public" / "db"
    destination_dir.mkdir(parents=True, exist_ok=True)
    destination = destination_dir / "sql-wasm.wasm"
    copy2(source, destination)
    return destination
