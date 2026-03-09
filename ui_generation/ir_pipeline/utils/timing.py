from __future__ import annotations

import logging
from contextlib import contextmanager
from time import perf_counter
from typing import Iterator


def _format_metadata(metadata: dict[str, object]) -> str:
    if not metadata:
        return ""
    parts = []
    for key, value in metadata.items():
        if value is None:
            continue
        parts.append(f"{key}={value}")
    return " | " + " | ".join(parts) if parts else ""


@contextmanager
def log_timed_step(
    logger: logging.Logger,
    step: str,
    **metadata: object,
) -> Iterator[None]:
    details = _format_metadata(metadata)
    logger.info("%s started%s", step, details)
    started = perf_counter()
    try:
        yield
    except Exception:
        elapsed_ms = (perf_counter() - started) * 1000
        logger.exception("%s failed | duration_ms=%.2f%s", step, elapsed_ms, details)
        raise
    else:
        elapsed_ms = (perf_counter() - started) * 1000
        logger.info("%s completed | duration_ms=%.2f%s", step, elapsed_ms, details)
