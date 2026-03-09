"""IRPatcher: applies a list of PatchOps to a raw IRBundle dict.

Usage
-----
    from ir_pipeline.patchops import IRPatcher, PatchFile

    patch_file = PatchFile.model_validate_json(Path("my.patch.json").read_text())
    patcher = IRPatcher(ir_dict)
    patched = patcher.apply(patch_file.patches)
"""

from __future__ import annotations

import copy
from typing import Any, Dict, List

from ir_pipeline.patchops.patch_schema import (
    AddComponent,
    AddEvent,
    AddLayoutChild,
    AddStateVar,
    AnyPatchOp,
    RemoveComponent,
    RemoveEvent,
    RemoveLayoutChild,
    RemoveStateVar,
    SetComponentBind,
    SetComponentEvent,
    SetComponentLabel,
    SetComponentProp,
    SetComponentStyle,
    SetComponentVisibility,
    SetDerivedExpr,
    SetEventMutation,
    SetLayoutGap,
    SetLayoutOrder,
    SetLayoutType,
    SetStateInitial,
    SetTheme,
)


class PatchError(Exception):
    """Raised when a patch operation cannot be applied."""


class PatchTargetError(PatchError):
    """A referenced ID does not exist in the IR."""


class PatchConflictError(PatchError):
    """A patch would create a duplicate ID or violate a constraint."""


class IRPatcher:
    """Mutates a copy of an IRBundle dict by applying patch operations.

    The original dict is never modified — apply() always works on a deep copy.
    """

    def __init__(self, ir_dict: Dict[str, Any]) -> None:
        self._original = ir_dict

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def apply(self, patches: List[AnyPatchOp]) -> Dict[str, Any]:
        """Apply all patches atomically (pre-flight validates every op first).

        Returns the patched IR dict. Raises PatchError on any failure before
        any mutation is written.
        """
        ir = copy.deepcopy(self._original)

        # Pre-flight: validate all targets exist before mutating anything
        for patch in patches:
            self._preflight(patch, ir)

        # Apply
        for patch in patches:
            self._dispatch(patch, ir)

        return ir

    # ------------------------------------------------------------------
    # Pre-flight validation (read-only, raises on bad refs)
    # ------------------------------------------------------------------

    def _preflight(self, patch: AnyPatchOp, ir: Dict[str, Any]) -> None:
        components = ir.get("component_ir", {}).get("components", {})
        layout_children = ir.get("layout_ir", {}).get("children", {})
        state = ir.get("data_ir", {}).get("state", {})
        derived = ir.get("data_ir", {}).get("derived", {})
        events = ir.get("behaviour_ir", {}).get("events", {})

        op = patch.op

        if op in (
            "set_component_prop", "set_component_style", "set_component_label",
            "set_component_bind", "set_component_event", "set_component_visibility",
            "remove_component",
        ):
            cid = patch.component_id  # type: ignore[attr-defined]
            if cid not in components:
                raise PatchTargetError(f"Component '{cid}' not found in component_ir.components")

        elif op == "add_component":
            if patch.component_id in components:
                raise PatchConflictError(f"Component '{patch.component_id}' already exists")
            if patch.container_id and patch.container_id not in layout_children:
                raise PatchTargetError(f"Container '{patch.container_id}' not found in layout_ir.children")

        elif op in ("set_layout_order", "set_layout_gap", "set_layout_type"):
            cid = patch.container_id  # type: ignore[attr-defined]
            if cid not in layout_children:
                raise PatchTargetError(f"Container '{cid}' not found in layout_ir.children")
            if op == "set_layout_order":
                unknown = [c for c in patch.order if c not in components]  # type: ignore[attr-defined]
                if unknown:
                    raise PatchTargetError(f"Unknown component(s) in order: {unknown}")

        elif op == "add_layout_child":
            if patch.container_id not in layout_children:
                raise PatchTargetError(f"Container '{patch.container_id}' not found in layout_ir.children")
            if patch.component_id not in components:
                raise PatchTargetError(f"Component '{patch.component_id}' not found in component_ir.components")

        elif op == "remove_layout_child":
            if patch.container_id not in layout_children:
                raise PatchTargetError(f"Container '{patch.container_id}' not found in layout_ir.children")

        elif op == "set_state_initial":
            if patch.var_id not in state:
                raise PatchTargetError(f"State variable '{patch.var_id}' not found in data_ir.state")

        elif op == "add_state_var":
            if patch.var_id in state:
                raise PatchConflictError(f"State variable '{patch.var_id}' already exists")

        elif op == "remove_state_var":
            if patch.var_id not in state:
                raise PatchTargetError(f"State variable '{patch.var_id}' not found in data_ir.state")

        elif op == "set_derived_expr":
            if patch.var_id not in derived:
                raise PatchTargetError(f"Derived variable '{patch.var_id}' not found in data_ir.derived")

        elif op == "set_event_mutation":
            if patch.event_id not in events:
                raise PatchTargetError(f"Event '{patch.event_id}' not found in behaviour_ir.events")

        elif op == "add_event":
            if patch.event_id in events:
                raise PatchConflictError(f"Event '{patch.event_id}' already exists")

        elif op == "remove_event":
            if patch.event_id not in events:
                raise PatchTargetError(f"Event '{patch.event_id}' not found in behaviour_ir.events")

    # ------------------------------------------------------------------
    # Dispatch
    # ------------------------------------------------------------------

    def _dispatch(self, patch: AnyPatchOp, ir: Dict[str, Any]) -> None:
        handlers = {
            "set_component_prop": self._set_component_prop,
            "set_component_style": self._set_component_style,
            "set_component_label": self._set_component_label,
            "set_component_bind": self._set_component_bind,
            "set_component_event": self._set_component_event,
            "set_component_visibility": self._set_component_visibility,
            "add_component": self._add_component,
            "remove_component": self._remove_component,
            "set_theme": self._set_theme,
            "set_layout_order": self._set_layout_order,
            "set_layout_gap": self._set_layout_gap,
            "set_layout_type": self._set_layout_type,
            "add_layout_child": self._add_layout_child,
            "remove_layout_child": self._remove_layout_child,
            "set_state_initial": self._set_state_initial,
            "add_state_var": self._add_state_var,
            "remove_state_var": self._remove_state_var,
            "set_derived_expr": self._set_derived_expr,
            "set_event_mutation": self._set_event_mutation,
            "add_event": self._add_event,
            "remove_event": self._remove_event,
        }
        handler = handlers.get(patch.op)
        if handler is None:
            raise PatchError(f"Unknown op: '{patch.op}'")
        handler(patch, ir)  # type: ignore[arg-type]

    # ------------------------------------------------------------------
    # Component handlers
    # ------------------------------------------------------------------

    def _set_component_prop(self, patch: SetComponentProp, ir: Dict[str, Any]) -> None:
        comp = ir["component_ir"]["components"][patch.component_id]
        comp.setdefault("props", {})[patch.prop] = patch.value

    def _set_component_style(self, patch: SetComponentStyle, ir: Dict[str, Any]) -> None:
        comp = ir["component_ir"]["components"][patch.component_id]
        comp.setdefault("styles", {}).update(patch.styles)

    def _set_component_label(self, patch: SetComponentLabel, ir: Dict[str, Any]) -> None:
        ir["component_ir"]["components"][patch.component_id]["label"] = patch.label

    def _set_component_bind(self, patch: SetComponentBind, ir: Dict[str, Any]) -> None:
        ir["component_ir"]["components"][patch.component_id]["bind"] = patch.bind

    def _set_component_event(self, patch: SetComponentEvent, ir: Dict[str, Any]) -> None:
        ir["component_ir"]["components"][patch.component_id][patch.handler] = patch.event_id

    def _set_component_visibility(self, patch: SetComponentVisibility, ir: Dict[str, Any]) -> None:
        ir["component_ir"]["components"][patch.component_id]["visible_when"] = patch.visible_when

    def _add_component(self, patch: AddComponent, ir: Dict[str, Any]) -> None:
        ir["component_ir"]["components"][patch.component_id] = patch.definition
        if patch.container_id:
            ir["layout_ir"]["children"][patch.container_id].append(patch.component_id)

    def _remove_component(self, patch: RemoveComponent, ir: Dict[str, Any]) -> None:
        ir["component_ir"]["components"].pop(patch.component_id, None)
        # Remove from all layout children lists
        for child_list in ir.get("layout_ir", {}).get("children", {}).values():
            if patch.component_id in child_list:
                child_list.remove(patch.component_id)

    def _set_theme(self, patch: SetTheme, ir: Dict[str, Any]) -> None:
        ir["component_ir"].setdefault("theme", {}).update(patch.theme)

    # ------------------------------------------------------------------
    # Layout handlers
    # ------------------------------------------------------------------

    def _set_layout_order(self, patch: SetLayoutOrder, ir: Dict[str, Any]) -> None:
        ir["layout_ir"]["children"][patch.container_id] = list(patch.order)

    def _set_layout_gap(self, patch: SetLayoutGap, ir: Dict[str, Any]) -> None:
        ir["layout_ir"].setdefault("layout", {}).setdefault(patch.container_id, {})["gap"] = patch.gap

    def _set_layout_type(self, patch: SetLayoutType, ir: Dict[str, Any]) -> None:
        ir["layout_ir"].setdefault("layout", {}).setdefault(patch.container_id, {})["type"] = patch.layout_type

    def _add_layout_child(self, patch: AddLayoutChild, ir: Dict[str, Any]) -> None:
        children = ir["layout_ir"]["children"][patch.container_id]
        if patch.position is None:
            children.append(patch.component_id)
        else:
            children.insert(patch.position, patch.component_id)

    def _remove_layout_child(self, patch: RemoveLayoutChild, ir: Dict[str, Any]) -> None:
        children = ir["layout_ir"]["children"].get(patch.container_id, [])
        if patch.component_id in children:
            children.remove(patch.component_id)

    # ------------------------------------------------------------------
    # Data handlers
    # ------------------------------------------------------------------

    def _set_state_initial(self, patch: SetStateInitial, ir: Dict[str, Any]) -> None:
        ir["data_ir"]["state"][patch.var_id]["initial"] = patch.initial

    def _add_state_var(self, patch: AddStateVar, ir: Dict[str, Any]) -> None:
        ir["data_ir"].setdefault("state", {})[patch.var_id] = patch.definition

    def _remove_state_var(self, patch: RemoveStateVar, ir: Dict[str, Any]) -> None:
        ir["data_ir"]["state"].pop(patch.var_id, None)

    def _set_derived_expr(self, patch: SetDerivedExpr, ir: Dict[str, Any]) -> None:
        ir["data_ir"]["derived"][patch.var_id]["expr"] = patch.expr

    # ------------------------------------------------------------------
    # Behaviour handlers
    # ------------------------------------------------------------------

    def _set_event_mutation(self, patch: SetEventMutation, ir: Dict[str, Any]) -> None:
        updates = ir["behaviour_ir"]["events"][patch.event_id].get("updates", [])
        for update in updates:
            if update.get("target") == patch.target:
                update["expr"] = patch.expr
                return
        # Target not found in existing updates — append a new one
        updates.append({"target": patch.target, "expr": patch.expr})
        ir["behaviour_ir"]["events"][patch.event_id]["updates"] = updates

    def _add_event(self, patch: AddEvent, ir: Dict[str, Any]) -> None:
        ir["behaviour_ir"].setdefault("events", {})[patch.event_id] = patch.definition

    def _remove_event(self, patch: RemoveEvent, ir: Dict[str, Any]) -> None:
        ir["behaviour_ir"]["events"].pop(patch.event_id, None)
        # Clear any component wiring that references this event
        for comp in ir.get("component_ir", {}).get("components", {}).values():
            for handler in ("onClick", "onChange", "onSubmit", "onHover"):
                if comp.get(handler) == patch.event_id:
                    comp[handler] = None