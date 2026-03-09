import argparse
import sys
from pathlib import Path

UI_GENERATION_DIR = Path(__file__).resolve().parents[1]
ROOT_DIR = UI_GENERATION_DIR.parent
DEFAULT_IR_INPUT = UI_GENERATION_DIR / "generated" / "ir" / "generated_ir.json"
DEFAULT_REACT_OUTPUT = UI_GENERATION_DIR / "generated" / "react" / "generated_app.tsx"

if str(UI_GENERATION_DIR) not in sys.path:
    sys.path.insert(0, str(UI_GENERATION_DIR))

from ir_pipeline.llm import DEFAULT_CLAUDE_MODEL
from ir_pipeline.services import convert_ir_file_to_react
from ir_pipeline.utils import configure_logging, get_logger, log_timed_step


def _resolve_path(path_str: str) -> Path:
    path = Path(path_str).expanduser()
    if path.is_absolute():
        return path
    return ROOT_DIR / path


def main() -> None:
    parser = argparse.ArgumentParser(description="Convert IRBundle JSON to React TSX using an LLM.")
    parser.add_argument(
        "--input",
        default=str(DEFAULT_IR_INPUT),
        help="Path to input IR JSON file (default: ui_generation/generated/ir/generated_ir.json).",
    )
    parser.add_argument(
        "--output",
        default=str(DEFAULT_REACT_OUTPUT),
        help="Path to output TSX file (default: ui_generation/generated/react/generated_app.tsx).",
    )
    parser.add_argument("--model", default=DEFAULT_CLAUDE_MODEL, help="LLM model name.")
    parser.add_argument(
        "--log-level",
        default="INFO",
        help="Log level for file and console logs (DEBUG, INFO, WARNING, ERROR).",
    )
    args = parser.parse_args()

    configure_logging(level=args.log_level)
    logger = get_logger("cli.ir_to_react")

    input_path = _resolve_path(args.input)
    output_path = _resolve_path(args.output)

    with log_timed_step(logger, "CLI command: IR to React", model=args.model):
        output_path = convert_ir_file_to_react(
            input_path=input_path,
            output_path=output_path,
            model_name=args.model,
        )


if __name__ == "__main__":
    main()
