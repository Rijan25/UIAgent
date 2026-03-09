"""Backward-compatible schema exports.

This module is kept for compatibility with existing imports.
The source of truth now lives in `ir_pipeline.schemas.ir_bundle`.
"""

import sys
from pathlib import Path

UI_GENERATION_DIR = Path(__file__).resolve().parents[1]
if str(UI_GENERATION_DIR) not in sys.path:
    sys.path.insert(0, str(UI_GENERATION_DIR))

from ir_pipeline.schemas.ir_bundle import *  # noqa: F403
