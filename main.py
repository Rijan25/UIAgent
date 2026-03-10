from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent
UI_GENERATION_DIR = ROOT_DIR / "ui_generation"
CLI_DIR = UI_GENERATION_DIR / "cli"
IR_GENERATION_SCRIPT = CLI_DIR / "ir_generation.py"
IR_TO_REACT_SCRIPT = CLI_DIR / "ir_to_react.py"
DEFAULT_IR_OUTPUT = UI_GENERATION_DIR / "generated" / "ir" / "generated_ir.json"
DEFAULT_REACT_OUTPUT = UI_GENERATION_DIR / "generated" / "react" / "generated_app.tsx"
FRONTEND_DIR_CANDIDATES = [
    ROOT_DIR / "ui-compiler" / "frontend",
    ROOT_DIR / "ui-compiler-poc" / "frontend",
]

if str(UI_GENERATION_DIR) not in sys.path:
    sys.path.insert(0, str(UI_GENERATION_DIR))

from ir_pipeline.utils import configure_logging, get_logger, log_timed_step


def _run_command(command: list[str], cwd: Path) -> None:
    subprocess.run(command, cwd=cwd, check=True)


def _preferred_python_executable() -> str:
    """
    Prefer the project's .venv interpreter for subprocess scripts.

    This makes `python main.py ...` work even when the user invoked the system
    Python (without deps) but has already installed deps into `.venv` via `uv sync`.
    """
    if os.environ.get("VIRTUAL_ENV"):
        return sys.executable

    venv_dir = ROOT_DIR / ".venv"
    if sys.platform.startswith("win"):
        candidates = [
            venv_dir / "Scripts" / "python.exe",
            venv_dir / "Scripts" / "python",
        ]
    else:
        candidates = [
            venv_dir / "bin" / "python3",
            venv_dir / "bin" / "python",
        ]

    for candidate in candidates:
        if candidate.exists():
            return str(candidate)

    return sys.executable


def _run_python_script(script: Path, args: list[str]) -> None:
    python_exe = _preferred_python_executable()
    _run_command([python_exe, str(script), *args], cwd=ROOT_DIR)


def _resolve_from_root(path_str: str) -> Path:
    path = Path(path_str).expanduser()
    if path.is_absolute():
        return path
    return ROOT_DIR / path


def _resolve_npm_command() -> list[str]:
    if sys.platform.startswith("win"):
        windows_candidates = [
            Path(r"C:\Program Files\nodejs\npm.cmd"),
            Path(r"C:\Program Files (x86)\nodejs\npm.cmd"),
        ]
        for candidate in windows_candidates:
            if candidate.exists():
                return [str(candidate)]

    for name in ["npm", "npm.cmd", "npm.exe"]:
        resolved = shutil.which(name)
        if resolved:
            return [resolved]

    if sys.platform.startswith("win"):
        return [os.environ.get("ComSpec", "cmd.exe"), "/c", "npm"]
    return ["npm"]


def _resolve_frontend_dir(frontend_dir_arg: str | None) -> Path:
    if frontend_dir_arg:
        candidate = Path(frontend_dir_arg)
        if not candidate.is_absolute():
            candidate = ROOT_DIR / candidate
        if (candidate / "package.json").exists():
            return candidate
        raise FileNotFoundError(f"No package.json found in frontend directory: {candidate}")

    for candidate in FRONTEND_DIR_CANDIDATES:
        if (candidate / "package.json").exists():
            return candidate
    raise FileNotFoundError(
        "Could not find frontend directory. Expected one of: "
        + ", ".join(str(path) for path in FRONTEND_DIR_CANDIDATES)
    )


def _build_ir_generation_args(args: argparse.Namespace) -> list[str]:
    command_args: list[str] = []
    if args.model:
        command_args.extend(["--model", args.model])
    command_args.extend(["--output", str(_resolve_from_root(args.ir_output) if args.ir_output else DEFAULT_IR_OUTPUT)])
    if args.overwrite is not None:
        command_args.append("--overwrite" if args.overwrite else "--no-overwrite")
    if args.images_dir:
        command_args.extend(["--images-dir", str(_resolve_from_root(args.images_dir))])
    if args.images_limit is not None:
        command_args.extend(["--images-limit", str(args.images_limit)])
    command_args.extend(["--log-level", args.log_level])
    return command_args


def _build_ir_to_react_args(args: argparse.Namespace) -> list[str]:
    command_args: list[str] = []
    if args.model:
        command_args.extend(["--model", args.model])

    input_path = args.react_input or args.ir_output
    resolved_input = _resolve_from_root(input_path) if input_path else DEFAULT_IR_OUTPUT
    command_args.extend(["--input", str(resolved_input)])

    resolved_output = _resolve_from_root(args.react_output) if args.react_output else DEFAULT_REACT_OUTPUT
    command_args.extend(["--output", str(resolved_output)])

    command_args.extend(["--log-level", args.log_level])
    return command_args


def _effective_react_output(args: argparse.Namespace) -> Path:
    if args.react_output:
        return _resolve_from_root(args.react_output)
    return DEFAULT_REACT_OUTPUT


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run full pipeline: natural-language UI request -> IR JSON -> React TSX."
    )
    parser.add_argument("--model", help="LLM model name used by both pipeline steps.")
    parser.add_argument(
        "--ir-output",
        help="Output path for generated IR JSON (forwarded to ir_generation.py --output).",
    )
    parser.add_argument(
        "--overwrite",
        action=argparse.BooleanOptionalAction,
        default=None,
        help="Whether to overwrite existing IR output (forwarded to ir_generation.py).",
    )
    parser.add_argument(
        "--images-dir",
        help="If set, generate IR from 1-3 reference images in this folder (forwarded to ir_generation.py).",
    )
    parser.add_argument(
        "--images-limit",
        type=int,
        default=None,
        help="Max images to load from --images-dir (forwarded to ir_generation.py).",
    )
    parser.add_argument(
        "--react-input",
        help="Input IR JSON path for React generation (defaults to --ir-output if provided).",
    )
    parser.add_argument(
        "--react-output",
        help="Output TSX path (forwarded to ir_to_react.py --output).",
    )
    parser.add_argument(
        "--frontend-dir",
        help="Frontend directory where `npm run dev` should run (must contain package.json).",
    )
    parser.add_argument(
        "--serve",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Run frontend dev server with `npm run dev` after React generation (default: True).",
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        help="Log level for file and console logs (DEBUG, INFO, WARNING, ERROR).",
    )
    args = parser.parse_args()

    configure_logging(level=args.log_level)
    logger = get_logger("pipeline.main")
    logger.info(
        "Pipeline run started | model=%s | serve=%s | images_dir=%s",
        args.model,
        args.serve,
        str(_resolve_from_root(args.images_dir)) if getattr(args, "images_dir", None) else None,
    )

    with log_timed_step(logger, "Pipeline step: IR generation"):
        _run_python_script(IR_GENERATION_SCRIPT, _build_ir_generation_args(args))

    with log_timed_step(logger, "Pipeline step: React generation"):
        _run_python_script(IR_TO_REACT_SCRIPT, _build_ir_to_react_args(args))

    if args.serve:
        frontend_dir = _resolve_frontend_dir(args.frontend_dir)
        frontend_app_path = frontend_dir / "src" / "App.tsx"
        react_output_path = _effective_react_output(args)
        if react_output_path.resolve() != frontend_app_path.resolve():
            with log_timed_step(logger, "Pipeline step: Sync generated React for preview"):
                frontend_app_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(react_output_path, frontend_app_path)
        npm_command = _resolve_npm_command()
        with log_timed_step(logger, "Pipeline step: Frontend dev server"):
            logger.info("Starting frontend dev server")
            _run_command([*npm_command, "run", "dev"], cwd=frontend_dir)

    logger.info("Pipeline run completed")


if __name__ == "__main__":
    main()
