"""ir_edit_service.py

Given the current IRBundle JSON and a plain-English edit request from the user,
calls the LLM to produce a minimal patch (list of PatchOps), applies it, and
returns the updated IRBundle.

This is the core of the chat-driven edit loop.
"""

from __future__ import annotations

import json
import re
from typing import Any

from pydantic import ValidationError

from ir_pipeline.llm import DEFAULT_CLAUDE_MODEL, build_chat_model
from ir_pipeline.patchops import IRPatcher, PatchError
from ir_pipeline.patchops.patch_schema import AnyPatchOp, PatchFile
from ir_pipeline.schemas import IRBundle
from ir_pipeline.utils import get_logger

logger = get_logger(__name__)


def _format_value(value: Any) -> str:
    """Compact and deterministic value rendering for chat summaries."""
    return json.dumps(value, ensure_ascii=True, separators=(",", ":"))


def _humanize_token(token: str) -> str:
    """Convert snake/camel identifiers into readable words."""
    text = re.sub(r"([a-z0-9])([A-Z])", r"\1 \2", token)
    text = text.replace("_", " ").replace("-", " ")
    return " ".join(text.split()).lower()


def _label_for_component(component_id: str, components: dict[str, Any]) -> str:
    comp = components.get(component_id, {})
    label = comp.get("label")
    if isinstance(label, str) and label.strip():
        return f"{label} ({component_id})"
    return component_id


def _label_for_container(container_id: str, components: dict[str, Any]) -> str:
    if container_id in components:
        return _label_for_component(container_id, components)
    return container_id


def _summarize_patch(patch: AnyPatchOp, patched_ir: dict[str, Any]) -> str:
    components = patched_ir.get("component_ir", {}).get("components", {})
    theme = patched_ir.get("component_ir", {}).get("theme", {})
    layout = patched_ir.get("layout_ir", {}).get("layout", {})
    children = patched_ir.get("layout_ir", {}).get("children", {})
    state = patched_ir.get("data_ir", {}).get("state", {})
    derived = patched_ir.get("data_ir", {}).get("derived", {})
    events = patched_ir.get("behaviour_ir", {}).get("events", {})

    op = patch.op

    if op == "set_component_prop":
        comp = components.get(patch.component_id, {})
        value = comp.get("props", {}).get(patch.prop)
        comp_name = _label_for_component(patch.component_id, components)
        return f"Updated {comp_name} {_humanize_token(patch.prop)} to {_format_value(value)}"

    if op == "set_component_style":
        comp = components.get(patch.component_id, {})
        styles = comp.get("styles", {})
        keys = list(patch.styles.keys())
        style_bits = [
            f"{_humanize_token(key)} {_format_value(styles.get(key))}" for key in keys
        ]
        comp_name = _label_for_component(patch.component_id, components)
        return f"Updated {comp_name} styles: {', '.join(style_bits)}"

    if op == "set_component_label":
        label = components.get(patch.component_id, {}).get("label")
        return f"Renamed {patch.component_id} to {_format_value(label)}"

    if op == "set_component_bind":
        bind = components.get(patch.component_id, {}).get("bind")
        comp_name = _label_for_component(patch.component_id, components)
        return f"Rebound {comp_name} to {_format_value(bind)}"

    if op == "set_component_event":
        handler_value = components.get(patch.component_id, {}).get(patch.handler)
        comp_name = _label_for_component(patch.component_id, components)
        return f"Set {comp_name} {_humanize_token(patch.handler)} to {_format_value(handler_value)}"

    if op == "set_component_visibility":
        visible_when = components.get(patch.component_id, {}).get("visible_when")
        comp_name = _label_for_component(patch.component_id, components)
        return f"Set {comp_name} visibility rule to {_format_value(visible_when)}"

    if op == "add_component":
        return f"Added component {patch.component_id}"

    if op == "remove_component":
        return f"Removed component {patch.component_id}"

    if op == "set_theme":
        keys = list(patch.theme.keys())
        rendered = ", ".join(
            f"{_humanize_token(key)} {_format_value(theme.get(key))}" for key in keys
        )
        return f"Updated theme: {rendered}"

    if op == "set_layout_order":
        current_order = children.get(patch.container_id, [])
        container_name = _label_for_container(patch.container_id, components)
        return f"Reordered {container_name} children ({len(current_order)} items)"

    if op == "set_layout_gap":
        gap = layout.get(patch.container_id, {}).get("gap")
        container_name = _label_for_container(patch.container_id, components)
        return f"Set {container_name} layout gap to {_format_value(gap)}"

    if op == "set_layout_type":
        layout_type = layout.get(patch.container_id, {}).get("type")
        container_name = _label_for_container(patch.container_id, components)
        return f"Set {container_name} layout type to {_format_value(layout_type)}"

    if op == "add_layout_child":
        current_order = children.get(patch.container_id, [])
        container_name = _label_for_container(patch.container_id, components)
        component_name = _label_for_component(patch.component_id, components)
        return f"Added {component_name} to {container_name} ({len(current_order)} items)"

    if op == "remove_layout_child":
        current_order = children.get(patch.container_id, [])
        container_name = _label_for_container(patch.container_id, components)
        return f"Removed {patch.component_id} from {container_name} ({len(current_order)} items)"

    if op == "set_state_initial":
        initial = state.get(patch.var_id, {}).get("initial")
        return f"Set state {patch.var_id} initial value to {_format_value(initial)}"

    if op == "add_state_var":
        return f"Added state var {patch.var_id}"

    if op == "remove_state_var":
        return f"Removed state var {patch.var_id}"

    if op == "set_derived_expr":
        expr = derived.get(patch.var_id, {}).get("expr")
        return f"Updated derived {patch.var_id} expression to {_format_value(expr)}"

    if op == "set_event_mutation":
        updates = events.get(patch.event_id, {}).get("updates", [])
        expr = None
        for update in updates:
            if update.get("target") == patch.target:
                expr = update.get("expr")
                break
        return f"Updated event {patch.event_id}: {patch.target} = {_format_value(expr)}"

    if op == "add_event":
        return f"Added event {patch.event_id}"

    if op == "remove_event":
        return f"Removed event {patch.event_id}"

    return f"Applied {op}"


def _build_applied_summary(patches: list[AnyPatchOp], patched_ir: dict[str, Any], max_items: int = 2) -> str:
    parts = [_summarize_patch(patch, patched_ir) for patch in patches]
    if not parts:
        return "No changes needed."
    if len(parts) <= max_items:
        return "; ".join(parts)
    head = "; ".join(parts[:max_items])
    return f"{head}; and {len(parts) - max_items} more change(s)"

# ---------------------------------------------------------------------------
# Prompt
# ---------------------------------------------------------------------------

_PATCH_OP_REFERENCE = """
Available patch operations (use the exact "op" values):

COMPONENT OPS  — target: component_ir.components
  set_component_prop      { op, component_id, prop, value }
  set_component_style     { op, component_id, styles: {key: value, ...} }   ← merged, not replaced
  set_component_label     { op, component_id, label }
  set_component_bind      { op, component_id, bind }
  set_component_event     { op, component_id, handler ("onClick"|"onChange"|"onSubmit"), event_id }
  set_component_visibility{ op, component_id, visible_when }
  add_component           { op, component_id, definition: {type, label, props, styles, ...}, container_id? }
  remove_component        { op, component_id }
  set_theme               { op, theme: {primaryColor?, borderRadius?, ...} }

LAYOUT OPS  — target: layout_ir
  set_layout_order        { op, container_id, order: [component_id, ...] }
  set_layout_gap          { op, container_id, gap: int }
  set_layout_type         { op, container_id, layout_type: "vertical"|"horizontal"|"grid"|"stack" }
  add_layout_child        { op, container_id, component_id, position?: int }
  remove_layout_child     { op, container_id, component_id }

DATA OPS  — target: data_ir
  set_state_initial       { op, var_id, initial }
  add_state_var           { op, var_id, definition: {type, initial} }
  remove_state_var        { op, var_id }
  set_derived_expr        { op, var_id, expr }

BEHAVIOUR OPS  — target: behaviour_ir
  set_event_mutation      { op, event_id, target, expr }
  add_event               { op, event_id, definition: {type: "mutation", updates: [{target, expr}]} }
  remove_event            { op, event_id }
""".strip()


def _build_edit_prompt(current_ir_json: str, user_request: str) -> str:
    return f"""You are an expert UI editor. The user wants to modify a generated UI.

Current IRBundle JSON:
{current_ir_json}

User request:
{user_request}

Your task: produce a JSON patch file that applies the minimal set of changes to satisfy the request.

{_PATCH_OP_REFERENCE}

Rules:
- Output ONLY a valid JSON object. No markdown, no explanation.
- The object must have a "patches" array containing patch operation objects.
- Use only component_id / container_id / var_id / event_id values that exist in the IR above,
  unless you are using an "add_*" operation to create a new one.
- For set_component_style, always merge — list only the keys you want to change.
- If the request cannot be expressed with these ops, return {{"patches": [], "description": "Cannot fulfil: <reason>"}}.
- Keep the patch minimal: only include the operations strictly required.

Output format:
{{
  "description": "one-line summary of what this patch does",
  "patches": [ ... ]
}}
""".strip()


# ---------------------------------------------------------------------------
# Service function
# ---------------------------------------------------------------------------

def generate_ir_edit(
    current_ir: dict[str, Any],
    user_request: str,
    model_name: str = DEFAULT_CLAUDE_MODEL,
    max_attempts: int = 3,
) -> tuple[dict[str, Any], str]:
    """Ask the LLM to produce a patch for `user_request`, apply it, return the new IR.

    Returns:
        (patched_ir_dict, summary_message)  — summary is shown back to the user.

    Raises:
        RuntimeError if the LLM fails to produce a valid patch after max_attempts.
    """
    logger.info(
        "IR edit started | model=%s | request_chars=%s",
        model_name,
        len(user_request),
    )

    model = build_chat_model(model_name=model_name, temperature=0)
    current_ir_json = json.dumps(current_ir, indent=2)
    prompt = _build_edit_prompt(current_ir_json, user_request)

    last_error: Exception | None = None

    for attempt in range(1, max_attempts + 1):
        logger.info("IR edit attempt %s/%s", attempt, max_attempts)
        response = model.invoke(prompt)
        raw_text = response.content if isinstance(response.content, str) else str(response.content)

        # Strip markdown fences if the model wraps output anyway
        raw_text = raw_text.strip()
        if raw_text.startswith("```"):
            lines = raw_text.splitlines()
            raw_text = "\n".join(
                line for line in lines if not line.strip().startswith("```")
            ).strip()

        try:
            patch_file = PatchFile.model_validate_json(raw_text)
        except (ValueError, ValidationError) as exc:
            last_error = exc
            logger.warning("Attempt %s: patch JSON invalid: %s", attempt, exc)
            # Retry with error context
            prompt = (
                f"{prompt}\n\nYour previous output was invalid JSON or failed schema validation:\n{exc}\n"
                f"Previous output:\n{raw_text}\n\nPlease correct it."
            )
            continue

        if not patch_file.patches:
            summary = patch_file.description or "No changes needed."
            logger.info("IR edit produced empty patch: %s", summary)
            return current_ir, summary

        patcher = IRPatcher(current_ir)
        try:
            patched = patcher.apply(patch_file.patches)
        except PatchError as exc:
            last_error = exc
            logger.warning("Attempt %s: patch application error: %s", attempt, exc)
            prompt = (
                f"{prompt}\n\nYour previous patch failed to apply:\n{exc}\n"
                f"Previous patch:\n{raw_text}\n\nPlease fix the patch."
            )
            continue

        # Validate the result against the full schema
        try:
            IRBundle.model_validate(patched)
        except ValidationError as exc:
            last_error = exc
            logger.warning("Attempt %s: patched IR failed schema validation: %s", attempt, exc)
            prompt = (
                f"{prompt}\n\nThe patched IR failed schema validation:\n{exc}\n"
                f"Previous patch:\n{raw_text}\n\nPlease fix the patch."
            )
            continue

        summary = _build_applied_summary(patch_file.patches, patched)
        logger.info("IR edit succeeded on attempt %s | ops=%s", attempt, len(patch_file.patches))
        return patched, summary

    raise RuntimeError(
        f"Failed to generate a valid IR edit after {max_attempts} attempts.\n"
        f"Last error: {last_error}"
    )
