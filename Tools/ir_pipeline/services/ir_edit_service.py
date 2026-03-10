"""ir_edit_service.py  (diff-merge mode)

Problem with full-IR-return approach
--------------------------------------
The IR JSON is large (~30k tokens). Asking the LLM to return the entire
updated IR means Bedrock must generate 30k+ tokens per edit — easily
exceeding any reasonable read timeout and burning unnecessary cost/latency.

Solution: diff-merge
--------------------------------------
1. Send the LLM a COMPACT SUMMARY of the IR (component IDs, state vars,
   events) — not the full JSON.
2. Ask it to return ONLY the changed sections as a partial IR dict.
3. Deep-merge that diff back into the full IR in Python.

Output tokens drop from ~30k to ~500-2000 per edit.
Latency drops from 60-160s to 3-10s.

The public signature is identical to previous versions:
    new_ir, summary = generate_ir_edit(current_ir, user_request, model_name)
"""

from __future__ import annotations

import copy
import json
from typing import Any

from pydantic import ValidationError

from ir_pipeline.llm import DEFAULT_CLAUDE_MODEL, build_chat_model
from ir_pipeline.schemas import IRBundle
from ir_pipeline.utils import (
    drop_extra_forbidden_fields,
    extract_json_object,
    get_logger,
    normalize_common_mismatches,
)

logger = get_logger(__name__)


# ---------------------------------------------------------------------------
# IR Summarizer — what the LLM sees as context
# ---------------------------------------------------------------------------

def _summarize_ir(ir: dict[str, Any]) -> str:
    """Compact, human-readable summary of the IR.

    This replaces sending the full IR JSON to the LLM, cutting input tokens
    by ~90% while giving the LLM everything it needs to reason about the UI.
    """
    lines: list[str] = []

    # Components
    components: dict = ir.get("component_ir", {}).get("components", {})
    lines.append("COMPONENTS:")
    for cid, c in components.items():
        ctype = c.get("type", "?")
        label = c.get("label", "")
        bind = c.get("bind", "")
        onclick = c.get("onClick", "")
        parts = [f"  {cid} ({ctype})"]
        if label:
            parts.append(f'"{label}"')
        if bind:
            parts.append(f"bind={bind}")
        if onclick:
            parts.append(f"onClick={onclick}")
        lines.append(" ".join(parts))

    # Layout
    lines.append("\nLAYOUT CONTAINERS:")
    for cid, children in ir.get("layout_ir", {}).get("children", {}).items():
        lines.append(f"  {cid} -> [{', '.join(children)}]")

    # State
    lines.append("\nSTATE:")
    for vid, s in ir.get("data_ir", {}).get("state", {}).items():
        lines.append(f"  {vid} ({s.get('type','?')}, initial={s.get('initial')!r})")

    # Events
    lines.append("\nEVENTS:")
    for eid in ir.get("behaviour_ir", {}).get("events", {}):
        lines.append(f"  {eid}")

    # Actions
    lines.append("\nACTIONS:")
    for aid in ir.get("behaviour_ir", {}).get("actions", {}):
        lines.append(f"  {aid}")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Deep merge utility
# ---------------------------------------------------------------------------

def _deep_merge(base: dict, diff: dict) -> dict:
    """Recursively merge diff into base, returning a new dict.

    - dict values are merged recursively
    - list values in diff REPLACE the base list entirely
    - scalar values in diff REPLACE the base scalar
    """
    result = copy.deepcopy(base)
    for key, val in diff.items():
        if isinstance(val, dict) and isinstance(result.get(key), dict):
            result[key] = _deep_merge(result[key], val)
        else:
            result[key] = copy.deepcopy(val)
    return result


# ---------------------------------------------------------------------------
# Prompts
# ---------------------------------------------------------------------------

_TOP_LEVEL_KEYS = (
    "page_ir", "data_ir", "data_fetch_ir", "data_model_ir",
    "behaviour_ir", "component_ir", "layout_ir",
    "navigation_ir", "realtime_ir", "metadata",
)

_DIFF_FORMAT_GUIDE = f"""
OUTPUT FORMAT — return ONLY the sections you are changing as a partial IR dict.

Rules:
- Return a JSON object containing ONLY the top-level IR keys that need updating.
- Within each top-level key, include ONLY the sub-keys you are changing.
- Do NOT repeat unchanged content.
- Allowed top-level keys: {', '.join(_TOP_LEVEL_KEYS)}

Examples of valid minimal diffs:

  Changing a button label:
  {{
    "component_ir": {{
      "components": {{
        "calculate_button": {{ "label": "Compute BMI" }}
      }}
    }}
  }}

  Adding a new component + wiring it into layout:
  {{
    "component_ir": {{
      "components": {{
        "reset_button": {{
          "type": "Button", "label": "Reset",
          "props": {{"type": "default"}}, "styles": {{}},
          "onClick": "resetForm"
        }}
      }}
    }},
    "layout_ir": {{
      "children": {{
        "button_row": ["calculate_button", "reset_button"]
      }}
    }},
    "behaviour_ir": {{
      "events": {{
        "resetForm": {{
          "type": "mutation",
          "updates": [{{"target": "state.selectedStudentId", "expr": "null"}}]
        }}
      }}
    }}
  }}

  Adding a state variable only:
  {{
    "data_ir": {{
      "state": {{
        "showModal": {{"type": "boolean", "initial": false, "required": false, "constraints": {{}}}}
      }}
    }}
  }}

IMPORTANT:
- layout_ir.children entries replace the ENTIRE children list for that container.
  Always include all existing children when modifying a container's children.
- Output ONLY valid JSON. No markdown. No explanation outside the JSON.
""".strip()


def _build_prompt(ir_summary: str, user_request: str) -> str:
    return f"""You are an expert UI engineer editing an IRBundle JSON.

=== CURRENT UI STRUCTURE ===
{ir_summary}

=== USER REQUEST ===
{user_request}

=== INSTRUCTIONS ===
{_DIFF_FORMAT_GUIDE}

Output the minimal diff JSON now:""".strip()


def _build_retry_prompt(
    original_prompt: str,
    bad_output: str,
    error: str,
) -> str:
    return f"""{original_prompt}

=== YOUR PREVIOUS OUTPUT WAS INVALID ===
Error: {error}

Previous output:
{bad_output}

Output a corrected diff JSON now. JSON only, no markdown.""".strip()


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def generate_ir_edit(
    current_ir: dict[str, Any],
    user_request: str,
    model_name: str = DEFAULT_CLAUDE_MODEL,
    max_attempts: int = 3,
) -> tuple[dict[str, Any], str]:
    """Edit the IR using a diff-merge strategy.

    The LLM receives a compact IR summary and returns only the changed
    sections. Python merges the diff into the full IR and validates the result.

    Returns:
        (updated_ir_dict, summary_message)

    Raises:
        RuntimeError if all attempts fail.
    """
    logger.info(
        "IR edit (diff-merge) started | model=%s | request=%r",
        model_name,
        user_request[:120],
    )

    model = build_chat_model(model_name=model_name, temperature=0)
    ir_summary = _summarize_ir(current_ir)
    prompt = _build_prompt(ir_summary, user_request)

    last_error = ""
    last_raw = ""

    for attempt in range(1, max_attempts + 1):
        logger.info("IR edit attempt %s/%s", attempt, max_attempts)

        response = model.invoke(prompt)
        raw_text = response.content if isinstance(response.content, str) else str(response.content)
        raw_text = raw_text.strip()

        # Strip markdown fences if present
        if raw_text.startswith("```"):
            raw_text = "\n".join(
                line for line in raw_text.splitlines()
                if not line.strip().startswith("```")
            ).strip()

        last_raw = raw_text

        # ── Parse the diff JSON ──────────────────────────────────────
        try:
            diff = json.loads(extract_json_object(raw_text))
        except Exception as exc:
            last_error = f"Could not parse diff JSON: {exc}"
            logger.warning("Attempt %s: %s", attempt, last_error)
            prompt = _build_retry_prompt(prompt, raw_text, last_error)
            continue

        # Reject if the LLM returned the full IR instead of a diff
        # (heuristic: a diff should not have all top-level keys AND be large)
        has_all_keys = all(k in diff for k in _TOP_LEVEL_KEYS)
        if has_all_keys:
            # Treat it as a full IR — still valid, just not optimal
            logger.info("Attempt %s: LLM returned full IR (not a diff) — using directly", attempt)
            merged = diff
        else:
            # Merge diff into a deep copy of the current IR
            merged = _deep_merge(current_ir, diff)

        # ── Normalise & validate ─────────────────────────────────────
        merged = normalize_common_mismatches(merged)

        try:
            bundle = IRBundle.model_validate(merged)
        except ValidationError as exc:
            if drop_extra_forbidden_fields(merged, exc):
                try:
                    bundle = IRBundle.model_validate(merged)
                except ValidationError as exc2:
                    last_error = f"Schema validation failed after auto-fix: {exc2}"
                    logger.warning("Attempt %s: %s", attempt, last_error)
                    prompt = _build_retry_prompt(prompt, raw_text, last_error)
                    continue
            else:
                last_error = f"Schema validation failed: {exc}"
                logger.warning("Attempt %s: %s", attempt, last_error)
                prompt = _build_retry_prompt(prompt, raw_text, last_error)
                continue

        # ── Success ──────────────────────────────────────────────────
        updated_ir = json.loads(bundle.model_dump_json())
        logger.info("IR edit (diff-merge) succeeded on attempt %s", attempt)
        return updated_ir, f"Done: {user_request}"

    raise RuntimeError(
        f"Failed to produce a valid IR diff after {max_attempts} attempts.\n"
        f"Last error: {last_error}\n"
        f"Last output:\n{last_raw}"
    )