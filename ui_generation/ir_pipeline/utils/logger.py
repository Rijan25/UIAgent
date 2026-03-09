from __future__ import annotations

import logging
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path
from uuid import uuid4

_LOGGER_NAME = "uiagent"
_MAX_BYTES = 1_000_000
_BACKUP_COUNT = 5
_DEFAULT_LEVEL = logging.INFO
_DEFAULT_CONSOLE_LOGGING = True


class _RunIdFilter(logging.Filter):
    def __init__(self, run_id: str) -> None:
        super().__init__()
        self._run_id = run_id

    def filter(self, record: logging.LogRecord) -> bool:
        if not hasattr(record, "run_id"):
            record.run_id = self._run_id
        return True


def _log_file_path() -> Path:
    app_dir = Path(__file__).resolve().parents[2]
    log_dir = app_dir / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    return log_dir / "uia.log"


def _resolve_level(level: int | str | None) -> int:
    if isinstance(level, int):
        return level

    if isinstance(level, str):
        candidate = level.strip().upper()
    else:
        candidate = os.getenv("UIAGENT_LOG_LEVEL", "").strip().upper()

    if candidate:
        resolved = getattr(logging, candidate, None)
        if isinstance(resolved, int):
            return resolved
    return _DEFAULT_LEVEL


def configure_logging(
    *,
    level: int | str | None = None,
    console_logging: bool = _DEFAULT_CONSOLE_LOGGING,
    run_id: str | None = None,
) -> logging.Logger:
    root_logger = logging.getLogger(_LOGGER_NAME)
    root_logger.setLevel(_resolve_level(level))

    if root_logger.handlers:
        return root_logger

    active_run_id = run_id or os.getenv("UIAGENT_RUN_ID") or uuid4().hex[:8]
    run_filter = _RunIdFilter(active_run_id)
    file_formatter = logging.Formatter(
        "%(asctime)s.%(msecs)03d | %(levelname)s | %(name)s | run=%(run_id)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    console_formatter = logging.Formatter("%(levelname)s | %(message)s")

    file_handler = RotatingFileHandler(
        _log_file_path(),
        maxBytes=_MAX_BYTES,
        backupCount=_BACKUP_COUNT,
        encoding="utf-8",
    )
    file_handler.setFormatter(file_formatter)
    file_handler.addFilter(run_filter)
    root_logger.addHandler(file_handler)

    if console_logging:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(console_formatter)
        console_handler.addFilter(run_filter)
        root_logger.addHandler(console_handler)

    root_logger.propagate = False
    return root_logger


def get_logger(name: str) -> logging.Logger:
    root_logger = logging.getLogger(_LOGGER_NAME)
    if not root_logger.handlers:
        root_logger = configure_logging()
    return root_logger.getChild(name)
