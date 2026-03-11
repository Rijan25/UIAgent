"""ir_edit_service.py  (full IR, invoke, explicit max_tokens)

Root cause of the "0 chunks" / empty response
-----------------------------------------------
Two problems compounded:

1. Message format mismatch
   The previous version passed a list of ("system", ...) / ("human", ...) tuples
   to model.stream(). The rest of the codebase uses model.invoke(plain_string).
   ChatBedrockConverse in langchain-aws 1.3.x does not yield tokens when the
   input format is wrong — it returns 0 chunks silently.

2. Missing max_tokens
   Bedrock requires max_tokens for Claude models. When unset it defaults to a
   small value (often 4096) which truncates a 30k-token IR output mid-JSON,
   producing unparseable output or an empty stream.

Fix
----
- Use model.invoke(string) — the same pattern used everywhere else in the codebase.
- Build the model with max_tokens=32000 (enough for a large full-IR response).
- The 300 s read_timeout already set in client.py handles the wall-clock time.
  invoke() with read_timeout=300 is fine — Bedrock streams internally and the
  HTTP connection stays open; only the first-byte timeout was ever the problem,
  and 300 s covers even the worst case.

Why full IR (not diff)
-----------------------
Diff/summary approaches require the LLM to reason about implicit context it
cannot see (e.g. prior layout decisions). Full IR means the LLM sees the
complete current state, so every edit is globally consistent by construction.

Public signature unchanged:
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
    """Single string prompt: system instructions + full IR + request.

    We embed the system prompt in the user message because model.invoke(string)
    does not accept a separate system parameter in this LangChain version.
    """
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

    Uses model.invoke() — the same pattern as the rest of the codebase.
    Sets max_tokens=32000 so Bedrock does not truncate large IR outputs.
    The 300 s read_timeout in client.py covers total generation time.

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

        response = model.invoke(prompt)
        raw_text = response.content if isinstance(response.content, str) else str(response.content)
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