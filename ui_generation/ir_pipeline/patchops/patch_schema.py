"""Patch operation schemas for PatchOps.

Each class maps to one edit operation on the IRBundle.
The `op` field is the discriminator used by IRPatcher to dispatch.
"""

from __future__ import annotations

from typing import Annotated, Any, Dict, List, Literal, Optional, Union

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Base
# ---------------------------------------------------------------------------

class PatchOp(BaseModel):
    """All patch operations inherit from this."""
    pass


# ---------------------------------------------------------------------------
# component_ir patches
# ---------------------------------------------------------------------------

class SetComponentProp(PatchOp):
    """Set a single key inside component.props."""
    op: Literal["set_component_prop"]
    component_id: str
    prop: str
    value: Any


class SetComponentStyle(PatchOp):
    """Merge style overrides into component.styles (deep merge, not replace)."""
    op: Literal["set_component_style"]
    component_id: str
    styles: Dict[str, Any]


class SetComponentLabel(PatchOp):
    """Convenience op: change component.label directly."""
    op: Literal["set_component_label"]
    component_id: str
    label: Optional[str]


class SetComponentBind(PatchOp):
    """Re-bind a component to a different state variable."""
    op: Literal["set_component_bind"]
    component_id: str
    bind: Optional[str]


class SetComponentEvent(PatchOp):
    """Re-wire onClick / onChange / onSubmit to a different event or action ID."""
    op: Literal["set_component_event"]
    component_id: str
    handler: Literal["onClick", "onChange", "onSubmit", "onHover"] = "onClick"
    event_id: Optional[str]  # None clears the handler


class SetComponentVisibility(PatchOp):
    """Set visible_when expression."""
    op: Literal["set_component_visibility"]
    component_id: str
    visible_when: Optional[str]


class AddComponent(PatchOp):
    """Insert a new component definition.

    `definition` must be a valid ComponentDef dict.
    If `container_id` is given, the component is appended to that container's children.
    """
    op: Literal["add_component"]
    component_id: str
    definition: Dict[str, Any]
    container_id: Optional[str] = None


class RemoveComponent(PatchOp):
    """Remove a component and clean up all layout children references."""
    op: Literal["remove_component"]
    component_id: str


class SetTheme(PatchOp):
    """Merge keys into component_ir.theme."""
    op: Literal["set_theme"]
    theme: Dict[str, Any]


# ---------------------------------------------------------------------------
# layout_ir patches
# ---------------------------------------------------------------------------

class SetLayoutOrder(PatchOp):
    """Replace the children list for a layout container with a new ordered list."""
    op: Literal["set_layout_order"]
    container_id: str
    order: List[str]


class SetLayoutGap(PatchOp):
    """Change the gap on a layout container."""
    op: Literal["set_layout_gap"]
    container_id: str
    gap: int


class SetLayoutType(PatchOp):
    """Change a container's layout direction."""
    op: Literal["set_layout_type"]
    container_id: str
    layout_type: Literal["vertical", "horizontal", "grid", "sidebar", "stack"]


class AddLayoutChild(PatchOp):
    """Append a component reference to a container's children list."""
    op: Literal["add_layout_child"]
    container_id: str
    component_id: str
    position: Optional[int] = None  # None = append; int = insert at index


class RemoveLayoutChild(PatchOp):
    """Remove a component reference from a container's children list."""
    op: Literal["remove_layout_child"]
    container_id: str
    component_id: str


# ---------------------------------------------------------------------------
# data_ir patches
# ---------------------------------------------------------------------------

class SetStateInitial(PatchOp):
    """Change the initial value of an existing state variable."""
    op: Literal["set_state_initial"]
    var_id: str
    initial: Any


class AddStateVar(PatchOp):
    """Add a new state variable. `definition` must be a valid StateFieldDef dict."""
    op: Literal["add_state_var"]
    var_id: str
    definition: Dict[str, Any]


class RemoveStateVar(PatchOp):
    """Remove a state variable."""
    op: Literal["remove_state_var"]
    var_id: str


class SetDerivedExpr(PatchOp):
    """Update the expression for a derived value."""
    op: Literal["set_derived_expr"]
    var_id: str
    expr: str


# ---------------------------------------------------------------------------
# behaviour_ir patches
# ---------------------------------------------------------------------------

class SetEventMutation(PatchOp):
    """Change the update expression for a specific target inside an event's updates list."""
    op: Literal["set_event_mutation"]
    event_id: str
    target: str   # the MutationUpdateDef.target to match
    expr: str     # new expression


class AddEvent(PatchOp):
    """Add a new event. `definition` must be a valid EventDef dict."""
    op: Literal["add_event"]
    event_id: str
    definition: Dict[str, Any]


class RemoveEvent(PatchOp):
    """Remove an event and clear component onClick/onChange wiring that references it."""
    op: Literal["remove_event"]
    event_id: str


# ---------------------------------------------------------------------------
# Discriminated union + PatchFile
# ---------------------------------------------------------------------------

AnyPatchOp = Annotated[
    Union[
        # component
        SetComponentProp,
        SetComponentStyle,
        SetComponentLabel,
        SetComponentBind,
        SetComponentEvent,
        SetComponentVisibility,
        AddComponent,
        RemoveComponent,
        SetTheme,
        # layout
        SetLayoutOrder,
        SetLayoutGap,
        SetLayoutType,
        AddLayoutChild,
        RemoveLayoutChild,
        # data
        SetStateInitial,
        AddStateVar,
        RemoveStateVar,
        SetDerivedExpr,
        # behaviour
        SetEventMutation,
        AddEvent,
        RemoveEvent,
    ],
    Field(discriminator="op"),
]


class PatchFile(BaseModel):
    """Top-level container for a .patch.json file."""
    description: Optional[str] = None
    patches: List[AnyPatchOp]