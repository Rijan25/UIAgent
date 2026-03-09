import json
from json import JSONDecodeError
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from ir_pipeline.llm import DEFAULT_CLAUDE_MODEL, build_chat_model
from ir_pipeline.prompts import build_base_prompt, build_retry_prompt, build_sql_retry_prompt
from ir_pipeline.schemas import IRBundle
from ir_pipeline.utils import (
    SQLValidationError,
    build_schema_prompt_context,
    drop_extra_forbidden_fields,
    ensure_external_db_snapshot,
    extract_json_object,
    get_logger,
    normalize_common_mismatches,
    sync_frontend_db_asset,
    sync_frontend_sql_wasm_asset,
    validate_and_normalize_sql_template,
    validate_sql_execution,
)

logger = get_logger(__name__)

TOOLS_DIR = Path(__file__).resolve().parents[2]
REPO_ROOT = TOOLS_DIR.parent
DEFAULT_SQLITE_DB_PATH = REPO_ROOT / "db" / "student_data.db"
DEFAULT_SNAPSHOT_PATH = REPO_ROOT / "db" / "external_db_snapshot.json"
FRONTEND_ROOT = REPO_ROOT / "ui-compiler-poc" / "frontend"
DEFAULT_FRONTEND_PUBLIC_DB_DIR = REPO_ROOT / "ui-compiler-poc" / "frontend" / "public" / "db"


def _as_int(value: Any, default: int) -> int:
    try:
        parsed = int(value)
        if parsed <= 0:
            return default
        return parsed
    except (TypeError, ValueError):
        return default


def _repo_relative_or_str(path: Path) -> str:
    try:
        return str(path.relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def _ensure_runtime_state_fields(bundle: IRBundle, default_page_size: int) -> None:
    data_ir = bundle.data_ir
    if not isinstance(data_ir, dict):
        return

    state = data_ir.setdefault("state", {})
    if not isinstance(state, dict):
        return

    def ensure_field(key: str, field_type: str, initial: Any) -> None:
        existing = state.get(key)
        if not isinstance(existing, dict):
            state[key] = {
                "type": field_type,
                "initial": initial,
                "required": False,
                "constraints": {},
            }
            return
        existing.setdefault("type", field_type)
        existing.setdefault("initial", initial)
        existing.setdefault("required", False)
        existing.setdefault("constraints", {})

    ensure_field("rows", "array", [])
    ensure_field("loading", "boolean", False)
    ensure_field("error", "string", "")
    ensure_field("page", "number", 1)
    ensure_field("pageSize", "number", default_page_size)
    ensure_field("total", "number", 0)


def _apply_sql_guardrails(
    bundle: IRBundle,
    snapshot: dict[str, Any] | None,
    db_path: Path | None,
    snapshot_path: Path | None,
) -> IRBundle:
    if snapshot is None or db_path is None or snapshot_path is None:
        return bundle

    data_model = bundle.data_model_ir
    if not isinstance(data_model, dict):
        return bundle

    sql_query = data_model.get("sql_query_ir")
    if sql_query is None:
        return bundle
    if not isinstance(sql_query, dict):
        raise SQLValidationError("data_model_ir.sql_query_ir must be an object.")

    sql_template = sql_query.get("sql_template")
    if not isinstance(sql_template, str) or not sql_template.strip():
        raise SQLValidationError("data_model_ir.sql_query_ir.sql_template must be a non-empty SQL string.")

    max_page_size = min(_as_int(sql_query.get("max_page_size"), 200), 200)
    default_page_size = _as_int(sql_query.get("default_page_size"), 50)
    if default_page_size > max_page_size:
        default_page_size = max_page_size

    raw_params = sql_query.get("params")
    allowed_params = raw_params if isinstance(raw_params, list) else None
    normalized = validate_and_normalize_sql_template(
        sql_template=sql_template,
        snapshot=snapshot,
        max_limit=max_page_size,
        allowed_params=allowed_params,
    )
    validate_sql_execution(
        sql_template=normalized["sql_template"],
        db_path=db_path,
        max_limit=max_page_size,
        params=normalized["params"],
    )

    sql_query["sql_template"] = normalized["sql_template"]
    sql_query["params"] = normalized["params"]
    sql_query["default_page_size"] = default_page_size
    sql_query["max_page_size"] = max_page_size

    snapshot_source = snapshot.get("source", {})
    data_model["external_source_ref"] = {
        "source_id": snapshot_source.get("source_id", "student_external"),
        "snapshot_path": _repo_relative_or_str(snapshot_path),
        "db_path": f"/db/{db_path.name}",
    }

    _ensure_runtime_state_fields(bundle=bundle, default_page_size=default_page_size)
    return bundle


def generate_ir_bundle(
    user_request: str,
    model_name: str = DEFAULT_CLAUDE_MODEL,
    max_attempts: int = 3,
) -> IRBundle:
    logger.info(
        "IR generation started | model=%s | max_attempts=%s | request_chars=%s",
        model_name,
        max_attempts,
        len(user_request),
    )
    model = build_chat_model(model_name=model_name, temperature=0)

    snapshot: dict[str, Any] | None = None
    schema_context: str | None = None
    if DEFAULT_SQLITE_DB_PATH.exists():
        try:
            snapshot = ensure_external_db_snapshot(
                db_path=DEFAULT_SQLITE_DB_PATH,
                snapshot_path=DEFAULT_SNAPSHOT_PATH,
                source_id="student_external",
                sample_rows_per_table=10,
            )
            schema_context = build_schema_prompt_context(snapshot=snapshot, include_samples=False)
            copied = sync_frontend_db_asset(
                db_path=DEFAULT_SQLITE_DB_PATH,
                frontend_public_db_dir=DEFAULT_FRONTEND_PUBLIC_DB_DIR,
            )
            wasm_copied = sync_frontend_sql_wasm_asset(frontend_root=FRONTEND_ROOT)
            logger.info(
                "External DB snapshot refreshed | db=%s | snapshot=%s | frontend_copy=%s | wasm_copy=%s",
                DEFAULT_SQLITE_DB_PATH,
                DEFAULT_SNAPSHOT_PATH,
                copied,
                wasm_copied,
            )
        except Exception as exc:
            logger.warning("Failed to refresh external DB snapshot: %s", exc)
    else:
        logger.info("SQLite DB not found for snapshot; continuing without DB schema context.")

    prompt = build_base_prompt(user_request=user_request, schema_context=schema_context)
    last_error = None
    last_raw_text = ""

    for attempt in range(1, max_attempts + 1):
        logger.info("IR generation attempt %s/%s", attempt, max_attempts)
        response = model.invoke(prompt)
        raw_text = response.content if isinstance(response.content, str) else str(response.content)
        last_raw_text = raw_text

        try:
            parsed = json.loads(extract_json_object(raw_text))
            normalized = normalize_common_mismatches(parsed)

            try:
                bundle = IRBundle.model_validate(normalized)
            except ValidationError as exc:
                if not drop_extra_forbidden_fields(normalized, exc):
                    raise
                bundle = IRBundle.model_validate(normalized)
            bundle = _apply_sql_guardrails(
                bundle=bundle,
                snapshot=snapshot,
                db_path=DEFAULT_SQLITE_DB_PATH if snapshot is not None else None,
                snapshot_path=DEFAULT_SNAPSHOT_PATH if snapshot is not None else None,
            )
            logger.info("IR generation succeeded on attempt %s", attempt)
            return bundle

        except (JSONDecodeError, ValidationError, SQLValidationError) as exc:
            last_error = exc
            logger.warning("IR generation attempt %s failed: %s", attempt, exc)
            if attempt == max_attempts:
                break
            if isinstance(exc, SQLValidationError):
                prompt = build_sql_retry_prompt(
                    user_request=user_request,
                    sql_error=exc,
                    raw_text=raw_text,
                    schema_context=schema_context,
                )
            else:
                prompt = build_retry_prompt(
                    user_request=user_request,
                    validation_error=exc,
                    raw_text=raw_text,
                    schema_context=schema_context,
                )

    logger.error(
        "IR generation failed after %s attempts | last_error=%s",
        max_attempts,
        last_error,
    )
    raise RuntimeError(
        f"Failed to generate a valid IRBundle after {max_attempts} attempts.\n"
        f"Last validation error: {last_error}\n"
        f"Last model output:\n{last_raw_text}"
    )


def write_ir_bundle(bundle: IRBundle, output_path: Path, overwrite: bool = True) -> None:
    if output_path.exists() and not overwrite:
        logger.error("IR JSON write blocked: file exists and overwrite is disabled | path=%s", output_path)
        raise FileExistsError(f"Output file already exists: {output_path}")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(bundle.model_dump_json(indent=2) + "\n", encoding="utf-8")
    logger.info("IR JSON written | path=%s", output_path.resolve())


def run_interactive_ir_generation(
    output_path: Path | None = None,
    model_name: str = DEFAULT_CLAUDE_MODEL,
    overwrite: bool = True,
) -> Path:
    logger.info("Interactive IR generation command started")
    user_request = input("Enter your UI request: ").strip()
    bundle = generate_ir_bundle(user_request=user_request, model_name=model_name)

    canonical_output = Path(__file__).resolve().parents[2] / "generated_ir.json"
    resolved_output = output_path or canonical_output

    write_ir_bundle(bundle=bundle, output_path=resolved_output, overwrite=overwrite)
    if resolved_output.resolve() != canonical_output.resolve():
        write_ir_bundle(bundle=bundle, output_path=canonical_output, overwrite=True)

    print(bundle.model_dump_json(indent=2))
    print(f"IR JSON written to: {resolved_output.resolve()}")
    if resolved_output.resolve() != canonical_output.resolve():
        print(f"IR JSON also written to: {canonical_output.resolve()} (overwrite=True)")
    logger.info("Interactive IR generation command completed")
    return resolved_output
