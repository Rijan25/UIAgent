import json
from json import JSONDecodeError
from pathlib import Path

from pydantic import ValidationError
from langchain_core.messages import HumanMessage

from ir_pipeline.llm import DEFAULT_CLAUDE_MODEL, build_chat_model
from ir_pipeline.prompts import build_base_prompt, build_retry_prompt
from ir_pipeline.schemas import IRBundle
from ir_pipeline.utils import (
    drop_extra_forbidden_fields,
    coerce_message_content_to_text,
    extract_json_object,
    get_logger,
    log_timed_step,
    normalize_common_mismatches,
)
from ir_pipeline.utils.images import (
    EncodedImage,
    collect_image_paths,
    encode_image,
    encoded_image_to_bedrock_block,
)

logger = get_logger(__name__)


def _invoke_ir_model(model: object, prompt_text: str, images: list[EncodedImage] | None) -> object:
    if not images:
        return model.invoke(prompt_text)  # type: ignore[attr-defined]

    content: list[dict] = [{"type": "text", "text": prompt_text}]
    for index, image in enumerate(images, start=1):
        content.append({"type": "text", "text": f"Image {index}: {image.path.name}"})
        content.append(encoded_image_to_bedrock_block(image))

    return model.invoke([HumanMessage(content=content)])  # type: ignore[attr-defined]


def generate_ir_bundle(
    user_request: str,
    images_dir: Path | None = None,
    images_limit: int | None = None,
    model_name: str = DEFAULT_CLAUDE_MODEL,
    max_attempts: int = 3,
) -> IRBundle:
    logger.info(
        "IR generation started | model=%s | max_attempts=%s | request_chars=%s | images_dir=%s",
        model_name,
        max_attempts,
        len(user_request),
        str(images_dir) if images_dir else None,
    )
    with log_timed_step(logger, "Build Bedrock chat model", model=model_name):
        model = build_chat_model(model_name=model_name, temperature=0)

    images: list[EncodedImage] | None = None
    if images_dir is not None:
        paths = collect_image_paths(images_dir=images_dir, limit=images_limit)
        if not paths:
            raise ValueError(f"No supported images found in {images_dir}. Expected png/jpg/webp/gif.")
        logger.info("Loading %s image(s) from %s", len(paths), images_dir)
        logger.info("Images: %s", ", ".join(path.name for path in paths))
        images = [encode_image(path) for path in paths]

        image_request = (
            """The UI specification is provided through the attached images. 
               These images may represent different screens, states, or interaction steps of the same interface.

               Carefully analyze all images and infer the underlying UI structure, layout, components, and possible user interactions. 
               Identify reusable UI patterns such as forms, tabs, tables, buttons, inputs, navigation elements, and computed fields.

               If multiple images represent variations of the same screen (e.g., different tab selections, filled vs empty states, or calculated fields), consolidate them into a single coherent UI definition.

               Based on this analysis, generate one consistent IRBundle that captures:
               - the overall page structure and layout
               - UI components and their hierarchy
               - data bindings and state fields
               - computed or system-generated fields
               - interaction behaviors and events
               - reusable styling or theme hints where applicable

              The resulting IRBundle should represent the complete UI logic and structure inferred from the images, not separate IRs for each image."""
        )

        if user_request.strip():
            image_request = f"{image_request}\nAdditional hint:\n{user_request.strip()}"
        prompt = build_base_prompt(image_request)
    else:
        prompt = build_base_prompt(user_request)
    last_error = None
    last_raw_text = ""

    for attempt in range(1, max_attempts + 1):
        logger.info("IR generation attempt %s/%s", attempt, max_attempts)
        with log_timed_step(logger, "Invoke IR generation model", attempt=attempt):
            response = _invoke_ir_model(model=model, prompt_text=prompt, images=images)
        raw_text = coerce_message_content_to_text(getattr(response, "content", response))
        last_raw_text = raw_text

        try:
            
            with log_timed_step(logger, "Parse and validate IR", attempt=attempt):
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
            logger.warning("IR generation attempt %s failed: %s", attempt, exc)
            if attempt == max_attempts:
                break
            retry_request = user_request
            if images_dir is not None and not retry_request.strip():
                retry_request = "Generate the IRBundle based on the attached images."
            prompt = build_retry_prompt(user_request=retry_request, validation_error=exc, raw_text=raw_text)

    logger.error(
        "IR generation failed after %s attempts | last_error=%s",
        max_attempts,
        last_error,
    )
    raise RuntimeError(
        f"Failed to generate a valid IRBundle after {max_attempts} attempts.\n"
        f"Last validation error: {last_error}\n"
        f"Last model output:\n{last_raw_text}"
    )


def write_ir_bundle(bundle: IRBundle, output_path: Path, overwrite: bool = True) -> None:
    if output_path.exists() and not overwrite:
        logger.error("IR JSON write blocked: file exists and overwrite is disabled")
        raise FileExistsError(f"Output file already exists: {output_path}")

    with log_timed_step(logger, "Write IR JSON"):
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(bundle.model_dump_json(indent=2) + "\n", encoding="utf-8")
    logger.info("IR JSON written")


def run_interactive_ir_generation(
    output_path: Path | None = None,
    model_name: str = DEFAULT_CLAUDE_MODEL,
    overwrite: bool = True,
    images_dir: Path | None = None,
    images_limit: int | None = None,
) -> Path:
    logger.info("Interactive IR generation command started")
    if images_dir is not None:
        # Image-first mode: read images, then allow the user to optionally request edits.
        user_request = input(
            "Optional edits (press Enter to keep images as-is): "
        ).strip()
        logger.info("Image-first mode | edits_provided=%s | edits_chars=%s", bool(user_request), len(user_request))
    else:
        user_request = input("Enter your UI request: ").strip()
        if not user_request:
            raise ValueError("UI request cannot be empty.")

    with log_timed_step(logger, "Generate IR bundle end-to-end", model=model_name):
        bundle = generate_ir_bundle(
            user_request=user_request,
            images_dir=images_dir,
            images_limit=images_limit,
            model_name=model_name,
        )

    canonical_output = Path(__file__).resolve().parents[2] / "generated" / "ir" / "generated_ir.json"
    resolved_output = output_path or canonical_output

    write_ir_bundle(bundle=bundle, output_path=resolved_output, overwrite=overwrite)
    if resolved_output.resolve() != canonical_output.resolve():
        write_ir_bundle(bundle=bundle, output_path=canonical_output, overwrite=True)

    logger.info("Interactive IR generation command completed")
    return resolved_output
