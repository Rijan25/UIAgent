# PatchOps Documentation

This document explains how PatchOps works end to end, from a `.patch.json` file to a validated patched IR.

## What PatchOps Is

PatchOps is a deterministic IR editing layer.

- Input: one or more patch files (`.patch.json`)
- Target: an existing `IRBundle` JSON file (default: `Tools/generated_ir.json`)
- Output: patched IR JSON (default: `Tools/patched_ir.json`)
- Optional: compile patched IR into React (`App.tsx`)

Entry point: `Tools/patch_ops.py`.

## Quick Start

From `Tools`:

```bash
uv run patch_ops.py --patch example.patch.json
```

From repo root:

```bash
uv run Tools/patch_ops.py --patch example.patch.json
```

Common options:

```bash
--patch FILE         # repeatable, applied in order
--ir-in FILE         # default generated_ir.json
--ir-out FILE        # default patched_ir.json
--dry-run            # print patched IR, do not write
--no-validate        # skip IRBundle schema validation
--compile            # run ir_to_react.py after patching
```

## Patch File Shape

Top-level schema:

```json
{
  "description": "optional text",
  "patches": [
    { "op": "set_component_label", "component_id": "add_button", "label": "Save" }
  ]
}
```

`patches` is a discriminated union on `op` (see `ir_pipeline/patchops/patch_schema.py`).

## Supported Operations

### Component IR

- `set_component_prop`
- `set_component_style` (merge/update keys, not full replacement)
- `set_component_label`
- `set_component_bind`
- `set_component_event`
- `set_component_visibility`
- `add_component`
- `remove_component` (also removes component references from layout children)
- `set_theme`

### Layout IR

- `set_layout_order`
- `set_layout_gap`
- `set_layout_type`
- `add_layout_child`
- `remove_layout_child`

### Data IR

- `set_state_initial`
- `add_state_var`
- `remove_state_var`
- `set_derived_expr`

### Behaviour IR

- `set_event_mutation` (updates matching target or appends a new update)
- `add_event`
- `remove_event` (also clears component event wiring that referenced the removed event)

## Execution Flow

PatchOps has a strict 6-stage pipeline:

1. CLI parse and path resolution
2. IR load (`--ir-in`)
3. Patch file parse + schema validation
4. Patch apply (atomic)
5. Optional IRBundle validation/normalization
6. Write output and optional compile

### 1) CLI Parse + Resolve

`patch_ops.py` resolves relative paths against the `Tools` directory, not the current shell directory.

### 2) Load IR

Base IR is read as JSON dict from `--ir-in` (default `generated_ir.json`).

### 3) Load and Parse Patch Files

Each `--patch` file is parsed via `PatchFile.model_validate_json(...)`.

- Invalid JSON or schema mismatch fails fast.
- Multiple patch files are concatenated in command-line order.

### 4) Apply Patches (Atomic Behavior)

`IRPatcher.apply(...)` does:

- deep-copy original IR
- preflight all patch ops (read-only checks)
- if preflight passes, dispatch/apply all ops in order

If any preflight check fails, no mutation is returned (because mutations never start).

### 5) Validate Output IR (Default On)

Unless `--no-validate`:

- normalize known IR mismatches
- validate against `IRBundle` schema
- if failure is only extra forbidden fields, drop those and retry validation once

Validation returns a normalized dict that becomes output.

### 6) Write / Dry-Run / Compile

- `--dry-run`: print patched JSON only
- otherwise write `--ir-out`
- if `--compile`, invoke `ir_to_react.py --input <ir_out>`

## Preflight Rules (Important)

Preflight catches invalid IDs and conflicts before apply:

- component-targeting ops require `component_id` to exist
- `add_component` fails if component already exists
- layout ops require `container_id` to exist in `layout_ir.children`
- `set_layout_order` requires every listed child component to exist
- state/event/derived targets must exist for set/remove ops
- add ops fail on duplicate IDs

Raised errors:

- `PatchTargetError`: referenced thing not found
- `PatchConflictError`: duplicate or constraint conflict
- `PatchError`: generic patch failure

## Operation Semantics and Side Effects

### Merge vs Replace

- `set_component_style` merges into `component.styles` (`dict.update`)
- `set_theme` merges into `component_ir.theme`
- `set_component_prop` sets one prop key only

### Cleanup Behaviors

- `remove_component` also removes it from all layout child arrays
- `remove_event` also clears component event handlers (`onClick`, `onChange`, `onSubmit`, `onHover`) when value equals removed event id

### Event Mutation Convenience

`set_event_mutation` finds update by `target`:

- if found: replace `expr`
- if missing: append new `{target, expr}`

## Ordering and Determinism

- Patch file order matters.
- Patch op order within each file matters.
- No randomness or LLM calls in PatchOps CLI path.
- Given same input IR + same ordered patches, output is deterministic.

## Troubleshooting

### `No such file or directory: patch_ops.py`

You likely ran from repo root without path. Use:

```bash
uv run Tools/patch_ops.py --patch example.patch.json
```

or run from `Tools`:

```bash
uv run patch_ops.py --patch example.patch.json
```

### `Component 'X' not found`

Patch references IDs not present in current `generated_ir.json`.

Inspect current IDs:

```bash
jq -r '.component_ir.components | keys[]' Tools/generated_ir.json
```

### Validation fails after successful apply

Patch ops were valid, but resulting IR failed full `IRBundle` schema validation.

Use:

```bash
uv run Tools/patch_ops.py --patch example.patch.json --no-validate
```

Then inspect/fix schema mismatch in IR or patch data.

## Testing PatchOps

Unit tests:

```bash
uv run python -m pytest Tools/tests/test_patchops.py -v
```

If pytest is missing:

```bash
uv pip install pytest
```

## How to Extend PatchOps

To add a new operation:

1. Add schema model in `patch_schema.py` with unique `op` literal.
2. Add it to `AnyPatchOp` union.
3. Add preflight rules in `IRPatcher._preflight`.
4. Add dispatch mapping in `IRPatcher._dispatch`.
5. Implement handler method on `IRPatcher`.
6. Add tests in `Tools/tests/test_patchops.py`.
7. Update this document.
