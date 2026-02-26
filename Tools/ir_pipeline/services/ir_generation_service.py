import json
import base64
import time
from json import JSONDecodeError
from pathlib import Path

from botocore.exceptions import ConnectTimeoutError, EndpointConnectionError, ReadTimeoutError
from langchain_core.messages import HumanMessage
from pydantic import ValidationError

from ir_pipeline.llm import DEFAULT_CLAUDE_MODEL, build_chat_model
from ir_pipeline.prompts import build_base_prompt, build_retry_prompt
from ir_pipeline.schemas import IRBundle
from ir_pipeline.utils import (
    drop_extra_forbidden_fields,
    extract_json_object,
    get_logger,
    normalize_common_mismatches,
)

logger = get_logger(__name__)
_IMAGE_MEDIA_TYPES = {
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".webp": "image/webp",
    ".gif": "image/gif",
}


def _is_transient_model_error(exc: Exception) -> bool:
    if isinstance(exc, (ReadTimeoutError, ConnectTimeoutError, EndpointConnectionError, TimeoutError)):
        return True

    message = str(exc).lower()
    transient_markers = (
        "timed out",
        "timeout",
        "temporarily unavailable",
        "service unavailable",
        "connection reset",
        "connection aborted",
        "throttl",
    )
    return any(marker in message for marker in transient_markers)


def _resolve_image_media_type(image_path: Path) -> str:
    media_type = _IMAGE_MEDIA_TYPES.get(image_path.suffix.lower())
    if media_type is None:
        supported = ", ".join(sorted(_IMAGE_MEDIA_TYPES))
        raise ValueError(
            f"Unsupported image extension '{image_path.suffix}' for {image_path}. "
            f"Supported extensions: {supported}"
        )
    return media_type


def _build_multimodal_message(prompt_text: str, image_path: Path | None):
    if image_path is None:
        return prompt_text

    media_type = _resolve_image_media_type(image_path)
    image_data = base64.b64encode(image_path.read_bytes()).decode("utf-8")
    message = HumanMessage(
        content=[
            {
                "type": "text",
                "text": (
                    f"{prompt_text}\n\n"
                    "The attached reference UI image is part of the user request. "
                    "Use both the text and image together."
                ),
            },
            {
                "type": "image",
                "source": {"type": "base64", "media_type": media_type, "data": image_data},
            },
        ]
    )
    return [message]


def _extract_response_text(response_content: object) -> str:
    if isinstance(response_content, str):
        return response_content

    if isinstance(response_content, list):
        text_chunks: list[str] = []
        for block in response_content:
            if isinstance(block, dict):
                text = block.get("text")
                if isinstance(text, str):
                    text_chunks.append(text)
        if text_chunks:
            return "\n".join(text_chunks)

    return str(response_content)


def generate_ir_bundle(
    user_request: str,
    model_name: str = DEFAULT_CLAUDE_MODEL,
    max_attempts: int = 3,
    reference_image_path: Path | None = None,
) -> IRBundle:
    logger.info(
        "IR generation started | model=%s | max_attempts=%s | request_chars=%s | has_image=%s",
        model_name,
        max_attempts,
        len(user_request),
        bool(reference_image_path),
    )
    model = build_chat_model(model_name=model_name, temperature=0)

    prompt = build_base_prompt(user_request)
    last_error = None
    last_raw_text = ""

    for attempt in range(1, max_attempts + 1):
        logger.info("IR generation attempt %s/%s", attempt, max_attempts)
        model_input = _build_multimodal_message(prompt, reference_image_path)
        try:
            response = model.invoke(model_input)
        except Exception as exc:
            if not _is_transient_model_error(exc):
                raise
            last_error = exc
            logger.warning("IR generation attempt %s invoke failed: %s", attempt, exc)
            if attempt == max_attempts:
                break
            backoff_seconds = min(2 ** (attempt - 1), 8)
            logger.info("Retrying invoke after %ss backoff", backoff_seconds)
            time.sleep(backoff_seconds)
            continue

        raw_text = _extract_response_text(response.content)
        last_raw_text = raw_text

        try:
            parsed = json.loads(extract_json_object(raw_text))
            normalized = normalize_common_mismatches(parsed)

            try:
                bundle = IRBundle.model_validate(normalized)
                logger.info("IR generation succeeded on attempt %s", attempt)
                return bundle
            except ValidationError as exc:
                if not drop_extra_forbidden_fields(normalized, exc):
                    raise
                bundle = IRBundle.model_validate(normalized)
                logger.info("IR generation succeeded on attempt %s after extra-field cleanup", attempt)
                return bundle

        except (JSONDecodeError, ValidationError) as exc:
            last_error = exc
            logger.warning("IR generation attempt %s validation failed: %s", attempt, exc)
            if attempt == max_attempts:
                break
            prompt = build_retry_prompt(user_request=user_request, validation_error=exc, raw_text=raw_text)

    logger.error(
        "IR generation failed after %s attempts | last_error=%s",
        max_attempts,
        last_error,
    )
    raise RuntimeError(
        f"Failed to generate a valid IRBundle after {max_attempts} attempts.\n"
        f"Last error: {last_error}\n"
        f"Last model output:\n{last_raw_text}"
    )


def write_ir_bundle(bundle: IRBundle, output_path: Path, overwrite: bool = True) -> None:
    if output_path.exists() and not overwrite:
        logger.error("IR JSON write blocked: file exists and overwrite is disabled | path=%s", output_path)
        raise FileExistsError(f"Output file already exists: {output_path}")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(bundle.model_dump_json(indent=2) + "\n", encoding="utf-8")
    logger.info("IR JSON written | path=%s", output_path.resolve())


def run_interactive_ir_generation(
    output_path: Path | None = None,
    model_name: str = DEFAULT_CLAUDE_MODEL,
    overwrite: bool = True,
    image_path: Path | None = None,
) -> Path:
    logger.info("Interactive IR generation command started")
    user_request = input("Enter your UI request: ").strip()
    if not user_request:
        raise ValueError("UI request cannot be empty.")
    resolved_image_path = image_path or Path(__file__).with_name("image.png")
    if not resolved_image_path.exists():
        raise FileNotFoundError(f"Reference image not found: {resolved_image_path}")

    bundle = generate_ir_bundle(
        user_request=user_request,
        model_name=model_name,
        reference_image_path=resolved_image_path,
    )

    canonical_output = Path(__file__).resolve().parents[2] / "generated_ir.json"
    resolved_output = output_path or canonical_output

    write_ir_bundle(bundle=bundle, output_path=resolved_output, overwrite=overwrite)
    if resolved_output.resolve() != canonical_output.resolve():
        write_ir_bundle(bundle=bundle, output_path=canonical_output, overwrite=True)

    print(bundle.model_dump_json(indent=2))
    print(f"IR JSON written to: {resolved_output.resolve()}")
    if resolved_output.resolve() != canonical_output.resolve():
        print(f"IR JSON also written to: {canonical_output.resolve()} (overwrite=True)")
    logger.info("Interactive IR generation command completed")
    return resolved_output
