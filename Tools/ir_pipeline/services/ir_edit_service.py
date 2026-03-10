"""ir_edit_service.py  (LLM-direct mode)

The LLM receives the current IR and the user's edit request, then returns
the complete updated IR JSON directly.  No patch schema, no deterministic
patcher — the LLM owns the full edit.

Why this is the right call for a POC
--------------------------------------
- Zero friction on complex requests (modals, new features, restructuring)
- No hallucinated-ID failures — the LLM edits what it can already see
- Faster iteration: one round-trip, one output, done
- The only guardrail that matters for a showcase is schema validation,
  which we still run so the React compiler always gets a valid IR

Public surface is identical to the old version so chat.py is unchanged:
    new_ir, summary = generate_ir_edit(current_ir, user_request, model_name)
"""

from __future__ import annotations

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
# Prompt
# ---------------------------------------------------------------------------

def _build_prompt(current_ir_json: str, user_request: str) -> str:
    return f"""You are an expert UI engineer working with an IRBundle JSON schema.

You will be given the current IR for a generated UI and a user request.
Your job is to return the complete updated IR that satisfies the request.

=== CURRENT IR ===
{current_ir_json}

=== USER REQUEST ===
{user_request}

=== INSTRUCTIONS ===
- Return ONLY the complete updated IRBundle JSON. No markdown, no explanation.
- Preserve every part of the IR that the request does not touch.
- You may add, remove, or modify any section: component_ir, layout_ir,
  data_ir, behaviour_ir, page_ir, navigation_ir, etc.
- Keep all existing IDs and wiring intact unless the request explicitly changes them.
- When adding new components, add them to layout_ir.children as well.
- When adding interactive elements (modals, popups, drawers), also add:
    - a boolean state var to control visibility
    - open/close events in behaviour_ir
    - visible_when on the component referencing the state var
- Output the same top-level keys as the input IR.
- Output valid JSON only.""".strip()


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

Please output a corrected complete IRBundle JSON now. JSON only, no markdown.""".strip()


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def generate_ir_edit(
    current_ir: dict[str, Any],
    user_request: str,
    model_name: str = DEFAULT_CLAUDE_MODEL,
    max_attempts: int = 3,
) -> tuple[dict[str, Any], str]:
    """Edit the IR using the LLM directly.

    The LLM receives the full current IR and returns a complete updated IR.
    Schema validation is run on the output; on failure the LLM is asked to
    self-correct with the validation error appended.

    Returns:
        (updated_ir_dict, summary_message)

    Raises:
        RuntimeError if all attempts fail.
    """
    logger.info(
        "IR edit (LLM-direct) started | model=%s | request=%r",
        model_name,
        user_request[:120],
    )

    model = build_chat_model(model_name=model_name, temperature=0)
    current_ir_json = json.dumps(current_ir, indent=2)
    prompt = _build_prompt(current_ir_json, user_request)

    last_error: str = ""
    last_raw: str = ""

    for attempt in range(1, max_attempts + 1):
        logger.info("IR edit attempt %s/%s", attempt, max_attempts)

        response = model.invoke(prompt)
        raw_text = response.content if isinstance(response.content, str) else str(response.content)
        raw_text = raw_text.strip()

        # Strip markdown fences — the LLM sometimes wraps output anyway
        if raw_text.startswith("```"):
            raw_text = "\n".join(
                line for line in raw_text.splitlines()
                if not line.strip().startswith("```")
            ).strip()

        last_raw = raw_text

        # ── Extract JSON ─────────────────────────────────────────────
        try:
            parsed = json.loads(extract_json_object(raw_text))
        except Exception as exc:
            last_error = f"Could not parse JSON from response: {exc}"
            logger.warning("Attempt %s: %s", attempt, last_error)
            prompt = _build_retry_prompt(prompt, raw_text, last_error)
            continue

        # ── Normalise common LLM quirks ──────────────────────────────
        parsed = normalize_common_mismatches(parsed)

        # ── Schema validation ────────────────────────────────────────
        try:
            bundle = IRBundle.model_validate(parsed)
        except ValidationError as exc:
            # Try dropping extra forbidden fields first (cheap auto-fix)
            if drop_extra_forbidden_fields(parsed, exc):
                try:
                    bundle = IRBundle.model_validate(parsed)
                except ValidationError as exc2:
                    last_error = f"Schema validation failed: {exc2}"
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
        logger.info("IR edit succeeded on attempt %s", attempt)
        return updated_ir, f"Done: {user_request}"

    raise RuntimeError(
        f"Failed to produce a valid IR after {max_attempts} attempts.\n"
        f"Last error: {last_error}\n"
        f"Last output:\n{last_raw}"
    )