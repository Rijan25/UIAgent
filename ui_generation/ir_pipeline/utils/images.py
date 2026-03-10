from __future__ import annotations

import base64
import mimetypes
from dataclasses import dataclass
from pathlib import Path


_SUPPORTED_IMAGE_MIME_TYPES: set[str] = {
    "image/png",
    "image/jpeg",
    "image/webp",
    "image/gif",
}


@dataclass(frozen=True)
class EncodedImage:
    path: Path
    media_type: str
    base64_data: str


def collect_image_paths(images_dir: Path, limit: int | None = None) -> list[Path]:
    if not images_dir.exists():
        raise FileNotFoundError(f"Images directory not found: {images_dir}")
    if not images_dir.is_dir():
        raise NotADirectoryError(f"Images path is not a directory: {images_dir}")
    if limit is not None and limit <= 0:
        raise ValueError("limit must be >= 1 or None")

    candidates: list[Path] = []
    for path in images_dir.iterdir():
        if not path.is_file():
            continue
        mime_type, _ = mimetypes.guess_type(str(path))
        if mime_type in _SUPPORTED_IMAGE_MIME_TYPES:
            candidates.append(path)

    candidates.sort(key=lambda p: p.name.lower())
    return candidates if limit is None else candidates[:limit]


def encode_image(path: Path) -> EncodedImage:
    if not path.exists():
        raise FileNotFoundError(f"Image not found: {path}")
    if not path.is_file():
        raise FileNotFoundError(f"Image is not a file: {path}")

    media_type, _ = mimetypes.guess_type(str(path))
    if not media_type or media_type not in _SUPPORTED_IMAGE_MIME_TYPES:
        raise ValueError(f"Unsupported image type for {path.name}: {media_type or 'unknown'}")

    base64_data = base64.b64encode(path.read_bytes()).decode("ascii")
    return EncodedImage(path=path, media_type=media_type, base64_data=base64_data)


def encoded_image_to_bedrock_block(image: EncodedImage) -> dict:
    # Bedrock Converse multimodal block format (supported by langchain-aws ChatBedrockConverse).
    return {
        "type": "image",
        "source": {
            "type": "base64",
            "media_type": image.media_type,
            "data": image.base64_data,
        },
    }
