import json
from pathlib import Path

from pydantic import ValidationError

from ir_pipeline.llm import build_chat_model
from ir_pipeline.prompts import build_react_prompt
from ir_pipeline.schemas import IRBundle
from ir_pipeline.utils import (
    coerce_message_content_to_text,
    extract_code_block,
    get_logger,
    log_timed_step,
)

logger = get_logger(__name__)


def load_ir_bundle(path: Path) -> IRBundle:
    with log_timed_step(logger, "Load IR JSON"):
        data = json.loads(path.read_text(encoding="utf-8"))
        bundle = IRBundle.model_validate(data)
    logger.info("Loaded IR JSON")
    return bundle


def generate_react_code(ir_bundle: IRBundle, model_name: str = "gpt-5.2") -> str:
    logger.info("React code generation started | model=%s", model_name)
    with log_timed_step(logger, "Build Bedrock chat model", model=model_name):
        model = build_chat_model(model_name=model_name, temperature=0)
    prompt = build_react_prompt(ir_bundle.model_dump_json(indent=2))

    with log_timed_step(logger, "Invoke React generation model", model=model_name):
        response = model.invoke(prompt)
    raw_text = coerce_message_content_to_text(getattr(response, "content", response))
    code = extract_code_block(raw_text)
    logger.info("React code generation completed")
    return code


def convert_ir_file_to_react(
    input_path: Path,
    output_path: Path,
    model_name: str = "gpt-5.2",
) -> Path:
    logger.info(
        "IR->React conversion started | model=%s",
        model_name,
    )
    if not input_path.exists():
        logger.error("IR->React conversion failed: input file not found")
        raise FileNotFoundError(f"Input file not found: {input_path}")

    try:
        ir_bundle = load_ir_bundle(input_path)
    except json.JSONDecodeError as exc:
        logger.error("IR->React conversion failed: invalid JSON | error=%s", exc)
        raise ValueError(f"Invalid JSON in {input_path}: {exc}") from exc
    except ValidationError as exc:
        logger.error("IR->React conversion failed: schema mismatch | error=%s", exc)
        raise ValueError(f"JSON does not match IRBundle schema: {exc}") from exc

    tsx_code = generate_react_code(ir_bundle=ir_bundle, model_name=model_name)
    with log_timed_step(logger, "Write React TSX"):
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(tsx_code + "\n", encoding="utf-8")
    logger.info("React TSX written")
    return output_path






# Run from the repo root (where main.py is): C:\Users\rijan\OneDrive\Desktop\UIAgent.

# Generate IR only (from images): uv run ui_generation/cli/ir_generation.py --images-dir ui_generation/uploads
# Full pipeline (IR -> React, no dev server): uv run  main.py --images-dir ui_generation/uploads --no-serve
# Full pipeline (and start frontend): uv run  main.py --images-dir ui_generation/uploads