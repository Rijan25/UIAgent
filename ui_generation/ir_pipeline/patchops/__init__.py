# CHANGED: added patchops exports below the existing IRBundle line
from ir_pipeline.schemas import IRBundle
from ir_pipeline.patchops.ir_patcher import IRPatcher, PatchConflictError, PatchError, PatchTargetError
from ir_pipeline.patchops.patch_schema import PatchFile

__all__ = [
    "IRBundle",
    "IRPatcher",
    "PatchFile",
    "PatchError",
    "PatchTargetError",
    "PatchConflictError",
]
