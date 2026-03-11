"""chat.py — Interactive chat-driven UI edit loop.

Workflow:
  1. Ask the user for the initial UI request (same as ir_generation.py).
  2. Generate the IR and compile it to App.tsx.
  3. Enter a REPL: user types an edit request → IR is updated → App.tsx is recompiled.
  4. Type 'exit' or Ctrl-C to quit.

Usage (from Tools/):
    uv run chat.py
    uv run chat.py --model global.anthropic.claude-sonnet-4-5-20250929-v1:0
    uv run chat.py --no-compile   (skip React compilation, only update the IR)
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


from ir_pipeline.llm import DEFAULT_CLAUDE_MODEL
from ir_pipeline.services import (
    convert_ir_file_to_react,
    generate_ir_bundle,
    generate_ir_edit,
    write_ir_bundle,
)
from ir_pipeline.utils import get_logger

logger = get_logger("chat")

TOOLS_DIR = Path(__file__).resolve().parent
REPO_ROOT = TOOLS_DIR.parent
IR_PATH = TOOLS_DIR / "generated_ir.json"
APP_TSX_PATH = REPO_ROOT / "ui-compiler-poc" / "frontend" / "src" / "App.tsx"

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
    print("\nAnything else is treated as an edit request.\n")


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
    parser.add_argument(
        "--no-compile",
        action="store_true",
        help="Skip React compilation after each edit (IR only).",
    )
    args = parser.parse_args()

    compile_enabled = not args.no_compile

    print(_DIVIDER)
    print("  UIAgent — Chat-driven UI Editor")
    print(_DIVIDER)
    print('Type "help" for commands, "exit" to quit.\n')

    # ── Step 1: Initial generation ────────────────────────────────────────
    initial_request = input("Describe the UI you want to build:\n> ").strip()
    if not initial_request:
        print("No request entered. Exiting.")
        return

    print("\n[chat] Generating IR …")
    try:
        bundle = generate_ir_bundle(user_request=initial_request, model_name=args.model)
    except Exception as exc:
        print(f"[chat] ERROR: IR generation failed: {exc}", file=sys.stderr)
        sys.exit(1)

    write_ir_bundle(bundle=bundle, output_path=IR_PATH, overwrite=True)
    print(f"[chat] IR written to: {IR_PATH}")

    if compile_enabled:
        _compile(IR_PATH, args.model)

    # Load as plain dict for the edit loop (patcher works on dicts, not IRBundle)
    current_ir: dict = json.loads(IR_PATH.read_text(encoding="utf-8"))
    history: list[str] = []

    print(f"\n{_DIVIDER}")
    print("UI generated! Now describe any changes you'd like.")
    print(_DIVIDER + "\n")

    # ── Step 2: Chat edit loop ────────────────────────────────────────────
    while True:
        try:
            user_input = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n[chat] Session ended.")
            break

        if not user_input:
            continue

        lowered = user_input.lower()

        # ── Built-in commands ──────────────────────────────────────────
        if lowered in ("exit", "quit"):
            print("[chat] Goodbye.")
            break

        if lowered == "help":
            _print_help()
            continue

        if lowered == "show ir":
            print(json.dumps(current_ir, indent=2))
            continue

        if lowered == "history":
            if not history:
                print("No edits yet this session.")
            else:
                for i, item in enumerate(history, 1):
                    print(f"  {i}. {item}")
            continue

        if lowered.startswith("save ir "):
            target = user_input[8:].strip()
            if not target:
                print("Usage: save ir <filepath>")
                continue
            out_path = Path(target) if Path(target).is_absolute() else TOOLS_DIR / target
            out_path.write_text(json.dumps(current_ir, indent=2) + "\n", encoding="utf-8")
            print(f"[chat] IR saved to: {out_path.resolve()}")
            continue

        # ── Edit request ───────────────────────────────────────────────
        print("[chat] Applying edit …")
        try:
            new_ir, summary = generate_ir_edit(
                current_ir=current_ir,
                user_request=user_input,
                model_name=args.model,
                edit_history=history,
            )
        except (RuntimeError, Exception) as exc:
            print(f"[chat] ERROR: {exc}", file=sys.stderr)
            logger.error("IR edit failed: %s", exc)
            print("[chat] The IR was NOT changed. Please try again.")
            continue

        current_ir = new_ir
        history.append(f"{user_input!r} → {summary}")
        print(f"[chat] ✓ {summary}")

        # Write updated IR to disk
        IR_PATH.write_text(json.dumps(current_ir, indent=2) + "\n", encoding="utf-8")

        if compile_enabled:
            _compile(IR_PATH, args.model)

        print()


if __name__ == "__main__":
    main()