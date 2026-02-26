import argparse
from pathlib import Path

from ir_pipeline.llm import DEFAULT_CLAUDE_MODEL
from ir_pipeline.services import run_interactive_ir_generation


def _resolve_output(path_str: str) -> Path:
    path = Path(path_str)
    if path.is_absolute():
        return path
    return Path(__file__).with_name(path_str)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate IRBundle JSON from a natural-language UI request.")
    parser.add_argument(
        "--output",
        default="generated_ir.json",
        help="Path to output IR JSON file (default: generated_ir.json in Tools).",
    )
    parser.add_argument(
        "--overwrite",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Whether to overwrite existing output file (default: True).",
    )
    parser.add_argument("--model", default=DEFAULT_CLAUDE_MODEL, help="LLM model name.")
    args = parser.parse_args()

    run_interactive_ir_generation(
        output_path=_resolve_output(args.output),
        model_name=args.model,
        overwrite=args.overwrite,
    )


if __name__ == "__main__":
    main()
