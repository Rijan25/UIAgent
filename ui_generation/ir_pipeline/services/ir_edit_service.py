"""ir_edit_service.py — LLM-driven full-IR edit (merged from feat/llmpatchops).

Design
------
The LLM receives the COMPLETE current IR and returns the COMPLETE updated IR.

Why full IR (not diff / patchops)
----------------------------------
Diff/summary approaches require the LLM to reason about implicit context it
cannot see (e.g. prior layout decisions). Full IR means the LLM sees the
complete current state, so every edit is globally consistent by construction.

This service replaces the old patchy patchops approach and plugs into the
ui_generation package layout from feat/poc.

Public signature:
    new_ir, summary = generate_ir_edit(current_ir, user_request, model_name)
"""

from __future__ import annotations

import json
from typing import Any

from pydantic import ValidationError

from ir_pipeline.llm import DEFAULT_CLAUDE_MODEL, build_chat_model
from ir_pipeline.schemas import IRBundle
from ir_pipeline.utils import (
    coerce_message_content_to_text,
    drop_extra_forbidden_fields,
    extract_json_object,
    get_logger,
    log_timed_step,
    normalize_common_mismatches,
)

logger = get_logger(__name__)

# Enough headroom for a large full-IR response (~30k output tokens).
# ChatBedrockConverse accepts max_tokens as a constructor kwarg.
_MAX_OUTPUT_TOKENS = 32_000

_SYSTEM_PROMPT = """You are an expert UI engineer editing an IRBundle JSON document.

You will receive the COMPLETE current IR and a description of the change the user wants.
Return the COMPLETE updated IR as valid JSON — every section, every key, every field.

Rules:
- Return the entire IRBundle JSON, not a partial diff.
- Preserve every existing component, state var, event, action, and layout entry
  unless the request explicitly removes it.
- When adding a new repeating entity (e.g. a new student card):
    * Add ALL required components matching the existing pattern exactly.
    * Add ALL required state vars matching the existing pattern exactly.
    * Extend EVERY event and action that covers similar entities to also cover
      the new one, using the exact same expression pattern.
    * Wire the new entity into layout_ir.children at the correct position,
      preserving the existing order of all other children.
- When reordering layout include ALL existing children in the new order.
  Never silently drop a child.
- When extending a behaviour_ir event or action updates array, copy all existing
  update objects and append the new ones. Do not omit existing updates.
- Output ONLY valid JSON. No markdown fences. No explanation. No preamble."""


def _build_prompt(current_ir: dict[str, Any], user_request: str) -> str:
    """Single string prompt: system instructions + full IR + request."""
    return (
        f"{_SYSTEM_PROMPT}\n\n"
        f"=== CURRENT IR ===\n"
        f"{json.dumps(current_ir, indent=2)}\n\n"
        f"=== USER REQUEST ===\n"
        f"{user_request}\n\n"
        f"Return the complete updated IR as JSON now."
    )


def generate_ir_edit(
    current_ir: dict[str, Any],
    user_request: str,
    model_name: str = DEFAULT_CLAUDE_MODEL,
    max_attempts: int = 3,
    edit_history: list[str] | None = None,  # kept for signature compat
) -> tuple[dict[str, Any], str]:
    """Edit the IR by sending the full IR to the LLM and getting the full IR back.

    Uses model.invoke() with max_tokens=32000 so Bedrock does not truncate large
    IR outputs. The extended read_timeout in client.py covers total generation time.

    Returns:
        (updated_ir_dict, summary_message)

    Raises:
        RuntimeError if all attempts fail.
    """
    logger.info(
        "IR edit (full IR) started | model=%s | request=%r",
        model_name,
        user_request[:120],
    )

    # max_tokens must be set at model construction time for ChatBedrockConverse
    with log_timed_step(logger, "Build Bedrock chat model for IR edit", model=model_name):
        model = build_chat_model(
            model_name=model_name,
            temperature=0,
            max_tokens=_MAX_OUTPUT_TOKENS,
        )

    prompt = _build_prompt(current_ir, user_request)
    last_error = ""
    last_raw = ""

    for attempt in range(1, max_attempts + 1):
        logger.info("IR edit attempt %s/%s", attempt, max_attempts)
        print(f"[edit] Calling model (attempt {attempt}/{max_attempts}) …", flush=True)

        with log_timed_step(logger, "Invoke IR edit model", attempt=attempt):
            response = model.invoke(prompt)

        raw_text = coerce_message_content_to_text(getattr(response, "content", response))
        raw_text = raw_text.strip()

        # Strip markdown fences if the model adds them despite instructions
        if raw_text.startswith("```"):
            raw_text = "\n".join(
                line for line in raw_text.splitlines()
                if not line.strip().startswith("```")
            ).strip()

        last_raw = raw_text

        # ── Parse ────────────────────────────────────────────────────
        try:
            updated = json.loads(extract_json_object(raw_text))
        except Exception as exc:
            last_error = f"Could not parse response as JSON: {exc}"
            logger.warning("Attempt %s: %s", attempt, last_error)
            prompt += (
                f"\n\nYour previous response could not be parsed as JSON.\n"
                f"Error: {last_error}\n"
                f"Output valid JSON only — no markdown, no preamble."
            )
            continue

        # ── Normalise & validate ─────────────────────────────────────
        updated = normalize_common_mismatches(updated)

        try:
            bundle = IRBundle.model_validate(updated)
        except ValidationError as exc:
            if drop_extra_forbidden_fields(updated, exc):
                try:
                    bundle = IRBundle.model_validate(updated)
                except ValidationError as exc2:
                    last_error = f"Schema validation failed after auto-fix: {exc2}"
                    logger.warning("Attempt %s: %s", attempt, last_error)
                    prompt += (
                        f"\n\nYour previous response failed schema validation.\n"
                        f"Error: {last_error}\n"
                        f"Return the corrected complete IR as JSON."
                    )
                    continue
            else:
                last_error = f"Schema validation failed: {exc}"
                logger.warning("Attempt %s: %s", attempt, last_error)
                prompt += (
                    f"\n\nYour previous response failed schema validation.\n"
                    f"Error: {last_error}\n"
                    f"Return the corrected complete IR as JSON."
                )
                continue

        # ── Success ──────────────────────────────────────────────────
        updated_ir = json.loads(bundle.model_dump_json())
        logger.info("IR edit succeeded on attempt %s", attempt)
        return updated_ir, f"Done: {user_request}"

    raise RuntimeError(
        f"Failed to produce a valid IR after {max_attempts} attempts.\n"
        f"Last error: {last_error}\n"
        f"Last raw output (first 2000 chars):\n{last_raw[:2000]}"
    )