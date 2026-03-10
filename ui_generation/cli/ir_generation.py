import argparse
import sys
from pathlib import Path

UI_GENERATION_DIR = Path(__file__).resolve().parents[1]
ROOT_DIR = UI_GENERATION_DIR.parent
DEFAULT_IR_OUTPUT = UI_GENERATION_DIR / "generated" / "ir" / "generated_ir.json"

if str(UI_GENERATION_DIR) not in sys.path:
    sys.path.insert(0, str(UI_GENERATION_DIR))

from ir_pipeline.llm import DEFAULT_CLAUDE_MODEL
from ir_pipeline.services import run_interactive_ir_generation
from ir_pipeline.utils import configure_logging, get_logger, log_timed_step


def _resolve_output(path_str: str) -> Path:
    path = Path(path_str).expanduser()
    if path.is_absolute():
        return path
    return ROOT_DIR / path


def _resolve_images_dir(path_str: str) -> Path:
    path = Path(path_str).expanduser()
    if path.is_absolute():
        return path
    return ROOT_DIR / path


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate IRBundle JSON from a natural-language UI request.")
    parser.add_argument(
        "--output",
        default=str(DEFAULT_IR_OUTPUT),
        help="Path to output IR JSON file (default: ui_generation/generated/ir/generated_ir.json).",
    )
    parser.add_argument(
        "--overwrite",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Whether to overwrite existing output file (default: True).",
    )
    parser.add_argument("--model", default=DEFAULT_CLAUDE_MODEL, help="LLM model name.")
    parser.add_argument(
        "--images-dir",
        help="If set, read 1-3 UI reference images from this folder and generate IR from the images.",
    )
    parser.add_argument(
        "--images-limit",
        type=int,
        default=None,
        help="Max number of images to load from --images-dir (default: all images in the folder).",
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        help="Log level for file and console logs (DEBUG, INFO, WARNING, ERROR).",
    )
    args = parser.parse_args()

    configure_logging(level=args.log_level)
    logger = get_logger("cli.ir_generation")
    output_path = _resolve_output(args.output)
    images_dir = _resolve_images_dir(args.images_dir) if args.images_dir else None

    with log_timed_step(logger, "CLI command: IR generation", model=args.model):
        run_interactive_ir_generation(
            output_path=output_path,
            model_name=args.model,
            overwrite=args.overwrite,
            images_dir=images_dir,
            images_limit=args.images_limit,
        )


if __name__ == "__main__":
    main()
