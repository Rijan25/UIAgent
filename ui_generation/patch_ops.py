"""patch_ops.py — CLI entrypoint for PatchOps.

Applies one or more .patch.json files to a generated IR and optionally
re-compiles the result to App.tsx.

Usage (from Tools/):
    uv run patch_ops.py --patch my_edits.patch.json
    uv run patch_ops.py --patch my_edits.patch.json --compile
    uv run patch_ops.py --patch my_edits.patch.json --dry-run
    uv run patch_ops.py --patch a.patch.json --patch b.patch.json --compile
"""

import argparse
import copy
import json
import subprocess
import sys
from pathlib import Path

from pydantic import ValidationError

from ir_pipeline.patchops import IRPatcher, PatchError
from ir_pipeline.patchops.patch_schema import PatchFile
from ir_pipeline.schemas import IRBundle
from ir_pipeline.utils import drop_extra_forbidden_fields, get_logger, normalize_common_mismatches

logger = get_logger("patchops.cli")


def _resolve(base: Path, raw: str) -> Path:
    p = Path(raw)
    return p if p.is_absolute() else (base / raw).resolve()


def _load_ir(path: Path) -> dict:
    if not path.exists():
        print(f"[patchops] ERROR: IR file not found: {path}", file=sys.stderr)
        sys.exit(1)
    return json.loads(path.read_text(encoding="utf-8"))


def _load_patch_file(path: Path) -> PatchFile:
    if not path.exists():
        print(f"[patchops] ERROR: Patch file not found: {path}", file=sys.stderr)
        sys.exit(1)
    try:
        return PatchFile.model_validate_json(path.read_text(encoding="utf-8"))
    except Exception as exc:
        print(f"[patchops] ERROR: Invalid patch file '{path}': {exc}", file=sys.stderr)
        sys.exit(1)


def _validate_ir(ir_dict: dict) -> dict:
    """Normalize and validate patched IR. Exits on failure; returns normalized dict."""
    normalized = normalize_common_mismatches(copy.deepcopy(ir_dict))
    try:
        IRBundle.model_validate(normalized)
    except ValidationError as exc:
        if drop_extra_forbidden_fields(normalized, exc):
            try:
                IRBundle.model_validate(normalized)
            except ValidationError as retry_exc:
                print(f"[patchops] ERROR: Patched IR failed schema validation:\n{retry_exc}", file=sys.stderr)
                sys.exit(1)
        else:
            print(f"[patchops] ERROR: Patched IR failed schema validation:\n{exc}", file=sys.stderr)
            sys.exit(1)
    except Exception as exc:
        print(f"[patchops] ERROR: Patched IR failed schema validation:\n{exc}", file=sys.stderr)
        sys.exit(1)
    return normalized


def main() -> None:
    tools_dir = Path(__file__).resolve().parent

    parser = argparse.ArgumentParser(
        description="Apply patch files to a generated IRBundle JSON."
    )
    parser.add_argument(
        "--patch",
        dest="patches",
        metavar="FILE",
        action="append",
        default=[],
        help="Path to a .patch.json file. Can be repeated to apply multiple patches in order.",
    )
    parser.add_argument(
        "--ir-in",
        default="generated_ir.json",
        help="Input IR JSON file (default: generated_ir.json in Tools).",
    )
    parser.add_argument(
        "--ir-out",
        default="patched_ir.json",
        help="Output patched IR JSON file (default: patched_ir.json in Tools).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the patched IR to stdout without writing any files.",
    )
    parser.add_argument(
        "--validate",
        action="store_true",
        default=True,
        help="Run IRBundle schema validation on the patched output (default: on).",
    )
    parser.add_argument(
        "--no-validate",
        dest="validate",
        action="store_false",
        help="Skip IRBundle schema validation.",
    )
    parser.add_argument(
        "--compile",
        action="store_true",
        help="After patching, invoke ir_to_react.py to regenerate App.tsx.",
    )
    args = parser.parse_args()

    if not args.patches:
        parser.error("Provide at least one --patch FILE argument.")

    # Load base IR
    ir_in_path = _resolve(tools_dir, args.ir_in)
    ir_dict = _load_ir(ir_in_path)
    print(f"[patchops] Loaded IR: {ir_in_path}")

    # Load and merge all patch files
    all_patches = []
    for patch_path_str in args.patches:
        patch_path = _resolve(tools_dir, patch_path_str)
        pf = _load_patch_file(patch_path)
        all_patches.extend(pf.patches)
        desc = f" ({pf.description})" if pf.description else ""
        print(f"[patchops] Loaded {len(pf.patches)} patch(es) from {patch_path}{desc}")

    # Apply
    patcher = IRPatcher(ir_dict)
    try:
        patched = patcher.apply(all_patches)
    except PatchError as exc:
        print(f"[patchops] ERROR: {exc}", file=sys.stderr)
        logger.error("Patch failed: %s", exc)
        sys.exit(1)

    print(f"[patchops] Applied {len(all_patches)} patch operation(s) successfully.")

    # Validate
    output_ir = patched
    if args.validate:
        output_ir = _validate_ir(patched)
        print("[patchops] IR schema validation passed.")

    if args.dry_run:
        print("\n--- Patched IR (dry run) ---")
        print(json.dumps(output_ir, indent=2))
        return

    # Write output
    ir_out_path = _resolve(tools_dir, args.ir_out)
    ir_out_path.write_text(json.dumps(output_ir, indent=2) + "\n", encoding="utf-8")
    print(f"[patchops] Patched IR written to: {ir_out_path}")
    logger.info("Patched IR written to %s (%d ops)", ir_out_path, len(all_patches))

    # Compile
    if args.compile:
        ir_to_react = tools_dir / "ir_to_react.py"
        cmd = [sys.executable, str(ir_to_react), "--input", str(ir_out_path)]
        print(f"[patchops] Compiling: {' '.join(cmd)}")
        result = subprocess.run(cmd, cwd=str(tools_dir))
        if result.returncode != 0:
            print("[patchops] ERROR: ir_to_react.py failed.", file=sys.stderr)
            sys.exit(result.returncode)
        print("[patchops] Compilation complete.")


if __name__ == "__main__":
    main()
