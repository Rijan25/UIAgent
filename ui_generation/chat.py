"""chat.py — Interactive chat-driven UI edit loop.

Workflow:
  1. Ask for the initial UI request (or use --images-dir for image-first mode).
  2. Generate the IR and compile it to App.tsx.
  3. REPL: user types an edit → full IR sent to LLM → updated IR back → recompile.
  4. Type 'exit' or Ctrl-C to quit.

Usage (from repo root):
    uv run ui_generation/chat.py
    uv run ui_generation/chat.py --images-dir ui_generation/uploads
    uv run ui_generation/chat.py --no-compile
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

UI_GENERATION_DIR = Path(__file__).resolve().parent
ROOT_DIR = UI_GENERATION_DIR.parent

if str(UI_GENERATION_DIR) not in sys.path:
    sys.path.insert(0, str(UI_GENERATION_DIR))

from ir_pipeline.llm import DEFAULT_CLAUDE_MODEL
from ir_pipeline.services import (
    convert_ir_file_to_react,
    generate_ir_bundle,
    generate_ir_edit,
    write_ir_bundle,
)
from ir_pipeline.utils import configure_logging, get_logger, log_timed_step

configure_logging()
logger = get_logger("chat")

IR_PATH = UI_GENERATION_DIR / "generated" / "ir" / "generated_ir.json"
APP_TSX_PATH = ROOT_DIR / "ui-compiler-poc" / "frontend" / "src" / "App.tsx"

_DIVIDER = "─" * 60
_COMMANDS = {
    "exit": "Quit the session.",
    "quit": "Quit the session.",
    "show ir": "Print the current IR to the terminal.",
    "save ir <file>": "Save the current IR to a custom path.",
    "history": "Show the list of edits made this session.",
    "help": "Show this help text.",
}


def _print_help() -> None:
    print("\nSpecial commands:")
    for cmd, desc in _COMMANDS.items():
        print(f"  {cmd:<22} {desc}")
    print("\nAnything else is treated as an edit request (full IR sent to LLM).\n")


def _compile(ir_path: Path, model_name: str) -> None:
    print("[chat] Compiling IR → App.tsx …")
    try:
        out = convert_ir_file_to_react(
            input_path=ir_path,
            output_path=APP_TSX_PATH,
            model_name=model_name,
        )
        print(f"[chat] App.tsx updated: {out.resolve()}")
    except Exception as exc:
        print(f"[chat] WARNING: React compilation failed: {exc}", file=sys.stderr)
        logger.warning("React compilation failed: %s", exc)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Interactive chat-driven UI generation and editing loop."
    )
    parser.add_argument("--model", default=DEFAULT_CLAUDE_MODEL, help="LLM model name.")
    parser.add_argument("--no-compile", action="store_true", help="Skip React compilation.")
    parser.add_argument("--images-dir", help="Generate initial IR from images in this folder.")
    parser.add_argument("--images-limit", type=int, default=None, help="Max images to load.")
    args = parser.parse_args()

    compile_enabled = not args.no_compile
    images_dir = Path(args.images_dir) if args.images_dir else None

    print(_DIVIDER)
    print("  UIAgent — Chat-driven UI Editor (Full IR Mode)")
    print(_DIVIDER)
    print('Type "help" for commands, "exit" to quit.\n')

    # ── Step 1: Initial generation ─────────────────────────────────────────
    if images_dir:
        print(f"[chat] Image-first mode | dir={images_dir}")
        user_request = input("Optional hint (press Enter to use images as-is): ").strip()
    else:
        user_request = input("What UI would you like to build? ").strip()
        if not user_request:
            print("[chat] No request provided. Exiting.")
            return

    print("[chat] Generating initial IR …")
    try:
        with log_timed_step(logger, "Initial IR generation", model=args.model):
            bundle = generate_ir_bundle(
                user_request=user_request,
                images_dir=images_dir,
                images_limit=args.images_limit,
                model_name=args.model,
            )
        write_ir_bundle(bundle, IR_PATH, overwrite=True)
        print(f"[chat] IR written → {IR_PATH.resolve()}")
    except Exception as exc:
        print(f"[chat] ERROR: IR generation failed: {exc}", file=sys.stderr)
        logger.exception("Initial IR generation failed")
        sys.exit(1)

    if compile_enabled:
        _compile(IR_PATH, args.model)

    current_ir: dict = json.loads(IR_PATH.read_text(encoding="utf-8"))
    edit_history: list[str] = []

    # ── Step 2: Edit REPL ──────────────────────────────────────────────────
    print(f"\n{_DIVIDER}")
    print("  Edit mode — describe a change or type 'help'")
    print(_DIVIDER)

    while True:
        try:
            raw = input("\n[edit] > ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n[chat] Bye!")
            break

        if not raw:
            continue

        cmd = raw.lower()

        if cmd in ("exit", "quit"):
            print("[chat] Bye!")
            break
        if cmd == "help":
            _print_help()
            continue
        if cmd == "show ir":
            print(json.dumps(current_ir, indent=2))
            continue
        if cmd == "history":
            if not edit_history:
                print("[chat] No edits yet.")
            else:
                for i, h in enumerate(edit_history, 1):
                    print(f"  {i}. {h}")
            continue
        if cmd.startswith("save ir "):
            dest = Path(raw[8:].strip())
            dest.write_text(json.dumps(current_ir, indent=2) + "\n", encoding="utf-8")
            print(f"[chat] IR saved to {dest.resolve()}")
            continue

        print(f"[edit] Sending full IR to LLM: {raw!r}")
        try:
            with log_timed_step(logger, "LLM IR edit", model=args.model):
                new_ir, summary = generate_ir_edit(
                    current_ir=current_ir,
                    user_request=raw,
                    model_name=args.model,
                )
            current_ir = new_ir
            edit_history.append(raw)
            IR_PATH.write_text(json.dumps(current_ir, indent=2) + "\n", encoding="utf-8")
            print(f"[edit] IR updated. {summary}")
            if compile_enabled:
                _compile(IR_PATH, args.model)
        except Exception as exc:
            print(f"[edit] ERROR: {exc}", file=sys.stderr)
            logger.exception("IR edit failed: %s", raw)


if __name__ == "__main__":
    main()