# from pydantic import BaseModel, Field, ConfigDict
# from typing import Dict, List, Optional, Literal, Any


# class StrictBase(BaseModel):
#     model_config = ConfigDict(extra="forbid")


# # -------------------------
# # DataIR
# # -------------------------
# class StateField(StrictBase):
#     type: Literal["number", "string", "boolean"]
#     initial: Any


# class DerivedField(StrictBase):
#     type: Literal["number", "string", "boolean"]
#     expr: str


# class DataIR(StrictBase):
#     state: Dict[str, StateField]
#     derived: Dict[str, DerivedField] = Field(default_factory=dict)


# # -------------------------
# # BehaviourIR
# # -------------------------
# class MutationUpdate(StrictBase):
#     target: str
#     expr: str


# class EventDefinition(StrictBase):
#     type: Literal["mutation"]
#     updates: List[MutationUpdate]


# class BehaviourIR(StrictBase):
#     events: Dict[str, EventDefinition]


# # -------------------------
# # ComponentIR
# # -------------------------
# class ThemeConfig(StrictBase):
#     primaryColor: Optional[str] = None


# class ComponentDefinition(StrictBase):
#     type: str
#     label: Optional[str] = None
#     bind: Optional[str] = None
#     onClick: Optional[str] = None
#     props: Dict[str, Any] = Field(default_factory=dict)
#     styles: Dict[str, Any] = Field(default_factory=dict)


# class ComponentIR(StrictBase):
#     library: Literal["antd"]  # <-- IMPORTANT
#     theme: Optional[ThemeConfig] = None
#     components: Dict[str, ComponentDefinition]


# # -------------------------
# # LayoutIR
# # -------------------------
# class LayoutConfig(StrictBase):
#     type: Literal["vertical", "horizontal", "grid"]
#     gap: Optional[int] = None


# class LayoutIR(StrictBase):
#     root: str
#     children: Dict[str, List[str]]
#     layout: Dict[str, LayoutConfig] = Field(default_factory=dict)


# # -------------------------
# # IRBundle
# # -------------------------
# class IRBundle(StrictBase):
#     data_ir: DataIR
#     behaviour_ir: BehaviourIR
#     component_ir: ComponentIR
#     layout_ir: LayoutIR



 
from __future__ import annotations

from pydantic import BaseModel, Field, ConfigDict
from typing import Dict, List, Optional, Literal, Any, Union


class StrictBase(BaseModel):
    model_config = ConfigDict(extra="forbid")


# -------------------------
# PageIR (page-level metadata)
# -------------------------
class StyleIR(StrictBase):
    tone: Optional[str] = None            # e.g. "clinical"
    theme: Optional[str] = None           # e.g. "light"
    density: Optional[str] = None         # e.g. "compact"
    color_intent: Optional[str] = None    # e.g. "high-contrast"


class AccessibilityIR(StrictBase):
    required_labels: List[str] = Field(default_factory=list)


class ResponsiveIR(StrictBase):
    breakpoints: Dict[str, Any] = Field(default_factory=dict)
    collapse_rules: List[Any] = Field(default_factory=list)
    hidden_on_small: List[str] = Field(default_factory=list)


class PageIR(StrictBase):
    page_goal: Optional[str] = None
    style: Optional[StyleIR] = None
    accessibility: Optional[AccessibilityIR] = None
    responsive: Optional[ResponsiveIR] = None
    constraints: List[Any] = Field(default_factory=list)


# -------------------------
# DataIR (UI state + derived)
# -------------------------
ScalarType = Literal["number", "string", "boolean"]
# If you want minimal change, keep ScalarType only.
# If you want more realistic dashboards, expand to:
DataType = Literal["number", "string", "boolean", "array", "object", "enum", "date"]


class StateField(StrictBase):
    type: DataType
    initial: Any
    required: bool = False
    constraints: Dict[str, Any] = Field(default_factory=dict)  # min/max/pattern/etc.


class DerivedField(StrictBase):
    type: DataType
    expr: str


class DataIR(StrictBase):
    state: Dict[str, StateField] = Field(default_factory=dict)
    derived: Dict[str, DerivedField] = Field(default_factory=dict)


# -------------------------
# EntityIR (records/schema/view model)
# -------------------------
class EntityIR(StrictBase):
    name: str
    fields: List[str] = Field(default_factory=list)
    computed: List[str] = Field(default_factory=list)
    display_fields: List[str] = Field(default_factory=list)
    filters: List[Any] = Field(default_factory=list)


class DataModelIR(StrictBase):
    entities: Dict[str, EntityIR] = Field(default_factory=dict)


# -------------------------
# BehaviourIR (actions + optional mutations)
# -------------------------
class MutationUpdate(StrictBase):
    target: str  # e.g. "state.selected_user_id" or "component.modal.open"
    expr: str    # expression language you define (js-like, python-like, etc.)


class EventDefinition(StrictBase):
    # keep your original mutation-only events for simple cases
    type: Literal["mutation"]
    updates: List[MutationUpdate]


class ActionDefinition(StrictBase):
    action_id: str
    trigger: str                   # e.g. "button_click"
    target_component_id: str        # e.g. "btn_calc"
    operation: str                 # e.g. "open_modal", "calculate_bmi"
    payload: Dict[str, Any] = Field(default_factory=dict)
    validation_rules: List[str] = Field(default_factory=list)
    requires_confirmation: bool = False

    # Optional: allow actions to also perform deterministic state/UI mutations
    updates: List[MutationUpdate] = Field(default_factory=list)


class FeedbackDefinition(StrictBase):
    action_id: str
    loading_indicator: Optional[str] = None   # e.g. "spinner"
    success_message: Optional[str] = None
    error_message: Optional[str] = None
    ui_updates: List[str] = Field(default_factory=list)  # e.g. ["refresh_table", "close_modal"]


class BehaviourIR(StrictBase):
    # Backward-compatible: keep events if you still use them
    events: Dict[str, EventDefinition] = Field(default_factory=dict)

    # New: action system matching your sample JSON
    actions: Dict[str, ActionDefinition] = Field(default_factory=dict)
    feedback: Dict[str, FeedbackDefinition] = Field(default_factory=dict)


# -------------------------
# ComponentIR
# -------------------------
class ThemeConfig(StrictBase):
    primaryColor: Optional[str] = None
    secondaryColor: Optional[str] = None
    fontFamily: Optional[str] = None
    borderRadius: Optional[int] = None
    


class ComponentDefinition(StrictBase):
    type: str
    label: Optional[str] = None
    bind: Optional[str] = None      # e.g. "entity.users" or "state.selected_user"
    onClick: Optional[str] = None   # e.g. action_id OR event_id (your choice)
    props: Dict[str, Any] = Field(default_factory=dict)
    styles: Dict[str, Any] = Field(default_factory=dict)


class ComponentIR(StrictBase):
    library: Literal["antd"]  # keep as you had
    theme: Optional[ThemeConfig] = None
    components: Dict[str, ComponentDefinition] = Field(default_factory=dict)


# -------------------------
# LayoutIR (tree + zones)
# -------------------------
class LayoutConfig(StrictBase):
    type: Literal["vertical", "horizontal", "grid"]
    gap: Optional[int] = None


class LayoutZone(StrictBase):
    zone_id: str
    component: str               # reference to component id/key in component_ir.components
    anchor: str                  # e.g. "bottom-right", "center"
    size_hint: str               # e.g. "full-width", "40%", "auto"
    z_layer: Literal["base", "overlay"]
    notes: Optional[str] = None


class LayoutIR(StrictBase):
    # Existing tree layout
    root: str
    children: Dict[str, List[str]] = Field(default_factory=dict)
    layout: Dict[str, LayoutConfig] = Field(default_factory=dict)

    # New zone layout (anchored + overlay)
    layout_zones: List[LayoutZone] = Field(default_factory=list)


# -------------------------
# IRBundle (extended)
# -------------------------
class IRBundle(StrictBase):
    page_ir: Optional[PageIR] = None

    data_ir: DataIR
    data_model_ir: DataModelIR = Field(default_factory=DataModelIR)

    behaviour_ir: BehaviourIR
    component_ir: ComponentIR
    layout_ir: LayoutIR