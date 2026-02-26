from __future__ import annotations
from enum import Enum
from typing import Any, Dict, List, Literal, Optional, Union

from pydantic import BaseModel, Field, ConfigDict

# ------------------------------------
# Strict base (no extra fields)
# ------------------------------------
class StrictBase(BaseModel):
    model_config = ConfigDict(extra="forbid")


# ------------------------------------
# Expression AST (safe, typed)
# ------------------------------------
# Based on common AST designs like ESTree but restricted + safe
class ExprNodeKind(str, Enum):
    literal = "Literal"
    identifier = "Identifier"
    binary = "BinaryExpression"
    logical = "LogicalExpression"
    conditional = "ConditionalExpression"
    call = "CallExpression"
    member = "MemberExpression"


class ExpressionNode(StrictBase):
    kind: ExprNodeKind


class LiteralNode(ExpressionNode):
    kind: Literal[ExprNodeKind.literal]
    value: Union[str, float, bool, None]


class IdentifierNode(ExpressionNode):
    kind: Literal[ExprNodeKind.identifier]
    name: str


class MemberNode(ExpressionNode):
    kind: Literal[ExprNodeKind.member]
    object: ExpressionNode
    property: ExpressionNode


class BinaryNode(ExpressionNode):
    kind: Literal[ExprNodeKind.binary]
    operator: Literal[
        "+", "-", "*", "/", "<", "<=", ">", ">=", "==", "!=", "===", "!=="
    ]
    left: ExpressionNode
    right: ExpressionNode


class LogicalNode(ExpressionNode):
    kind: Literal[ExprNodeKind.logical]
    operator: Literal["&&", "||"]
    left: ExpressionNode
    right: ExpressionNode


class ConditionalNode(ExpressionNode):
    kind: Literal[ExprNodeKind.conditional]
    test: ExpressionNode
    consequent: ExpressionNode
    alternate: ExpressionNode


class CallNode(ExpressionNode):
    kind: Literal[ExprNodeKind.call]
    callee: IdentifierNode
    arguments: List[ExpressionNode]


ExprAST = Union[
    LiteralNode,
    IdentifierNode,
    MemberNode,
    BinaryNode,
    LogicalNode,
    ConditionalNode,
    CallNode,
]

# ------------------------------------
# Page-level policy
# ------------------------------------
class StyleIR(StrictBase):
    tone: Optional[str] = None
    theme: Optional[str] = None
    density: Optional[str] = None
    color_intent: Optional[str] = None


class AccessibilityIR(StrictBase):
    required_labels: List[str] = Field(default_factory=list)


class ResponsiveIR(StrictBase):
    breakpoints: Dict[str, int] = Field(default_factory=dict)
    collapse_rules: List[Dict[str, Any]] = Field(default_factory=list)
    hidden_on_small: List[str] = Field(default_factory=list)


class PageIR(StrictBase):
    page_goal: Optional[str] = None
    style: Optional[StyleIR] = None
    accessibility: Optional[AccessibilityIR] = None
    responsive: Optional[ResponsiveIR] = None
    constraints: List[str] = Field(default_factory=list)


# ------------------------------------
# Data state + derived
# ------------------------------------
DataType = Literal[
    "number", "string", "boolean", "array", "object", "enum", "date"
]


class StateField(StrictBase):
    type: DataType
    initial: Any
    required: bool = False
    constraints: Dict[str, Any] = Field(default_factory=dict)
    description: Optional[str] = None


class DerivedField(StrictBase):
    type: DataType
    expr: ExprAST
    description: Optional[str] = None


class DataStateIR(StrictBase):
    state: Dict[str, StateField] = Field(default_factory=dict)
    derived: Dict[str, DerivedField] = Field(default_factory=dict)


class EntityIR(StrictBase):
    name: str
    fields: List[str] = Field(default_factory=list)
    computed: List[str] = Field(default_factory=list)
    display_fields: List[str] = Field(default_factory=list)
    filters: List[Dict[str, Any]] = Field(default_factory=list)
    sort_by: Optional[str] = None
    pagination: Optional[bool] = None


class DataModelIR(StrictBase):
    entities: Dict[str, EntityIR] = Field(default_factory=dict)


# ------------------------------------
# Components / UI
# ------------------------------------
class CSSValueType(str, Enum):
    px = "px"
    em = "em"
    rem = "rem"
    percent = "%"
    color = "color"
    keyword = "keyword"


class CSSValue(StrictBase):
    value: Union[int, float, str]
    unit: Optional[CSSValueType] = None


class ThemeConfig(StrictBase):
    primaryColor: Optional[str] = None
    secondaryColor: Optional[str] = None
    fontFamily: Optional[str] = None
    borderRadius: Optional[int] = None


class ComponentDefinition(StrictBase):
    type: str
    label: Optional[str] = None
    bind: Optional[str] = None
    onClick: Optional[str] = None
    props: Dict[str, Any] = Field(default_factory=dict)
    styles: Dict[str, CSSValue] = Field(default_factory=dict)
    a11y_labels: List[str] = Field(default_factory=list)


class ComponentIR(StrictBase):
    library: Literal["antd"] = "antd"
    theme: Optional[ThemeConfig] = None
    components: Dict[str, ComponentDefinition] = Field(default_factory=dict)


# ------------------------------------
# UI tree
# ------------------------------------
class ComponentNodeIR(StrictBase):
    node_id: str
    component_id: str
    kind: Optional[str] = None
    parent_id: Optional[str] = None
    children: List[str] = Field(default_factory=list)
    zone_id: Optional[str] = None


class ComponentTreeIR(StrictBase):
    root_id: str = "root"
    nodes: Dict[str, ComponentNodeIR] = Field(default_factory=dict)


# ------------------------------------
# Layout with zones
# ------------------------------------
class LayoutType(str, Enum):
    vertical = "vertical"
    horizontal = "horizontal"
    grid = "grid"


class LayoutConfig(StrictBase):
    type: LayoutType
    gap: Optional[int] = None
    columns: Optional[int] = None
    rowGap: Optional[int] = None
    colGap: Optional[int] = None


class PlacementIR(StrictBase):
    strategy: Literal["anchor", "overlay", "auto_flow"] = "auto_flow"
    justify: Literal["start", "center", "end", "stretch"] = "start"
    align: Literal["start", "center", "end", "stretch"] = "start"
    width: Optional[str] = None
    height: Optional[str] = None
    z_index_token: Optional[str] = None


class LayoutZoneIR(StrictBase):
    zone_id: str
    node_id: str
    anchor: Optional[str] = None
    size_hint: Optional[str] = None
    z_layer: Literal["base", "overlay"] = "base"
    placement: PlacementIR = Field(default_factory=PlacementIR)
    notes: Optional[str] = None


class LayoutIR(StrictBase):
    strategy: Literal["desktop-first", "mobile-first", "adaptive"] = "desktop-first"
    breakpoints: Dict[str, int] = Field(default_factory=dict)
    layout: Dict[str, LayoutConfig] = Field(default_factory=dict)
    zones: Dict[str, LayoutZoneIR] = Field(default_factory=dict)


# ------------------------------------
# Behavior (typed actions & updates)
# ------------------------------------
class PayloadType(str, Enum):
    state_ref = "state_ref"
    derived_ref = "derived_ref"
    constant = "constant"
    event_ref = "event_ref"


class PayloadValue(StrictBase):
    type: PayloadType
    key: str
    value: Optional[Any] = None


class MutationUpdate(StrictBase):
    target: str
    expr: ExprAST


class EventDefinition(StrictBase):
    type: Literal["mutation"] = "mutation"
    updates: List[MutationUpdate] = Field(default_factory=list)


class ActionDefinition(StrictBase):
    action_id: str
    trigger: str
    target_node_id: Optional[str] = None
    target_component_id: Optional[str] = None
    operation: str
    payload: List[PayloadValue] = Field(default_factory=list)
    validation: List[ExprAST] = Field(default_factory=list)
    requires_confirmation: bool = False
    updates: List[MutationUpdate] = Field(default_factory=list)


class FeedbackDefinition(StrictBase):
    action_id: str
    loading: Optional[str] = None
    success: Optional[str] = None
    error: Optional[str] = None
    messages: List[str] = Field(default_factory=list)


class BehaviorIR(StrictBase):
    events: Dict[str, EventDefinition] = Field(default_factory=dict)
    actions: Dict[str, ActionDefinition] = Field(default_factory=dict)
    feedback: Dict[str, FeedbackDefinition] = Field(default_factory=dict)
    constraints: List[ExprAST] = Field(default_factory=list)


# ------------------------------------
# Patch ops (JSON-patch style)
# ------------------------------------
class PatchOpBase(StrictBase):
    op: Literal["add", "remove", "replace", "move", "copy", "test"]
    path: str  # JSON pointer syntax


class PatchOpAdd(PatchOpBase):
    op: Literal["add"]
    value: Any


class PatchOpRemove(PatchOpBase):
    op: Literal["remove"]


class PatchOpReplace(PatchOpBase):
    op: Literal["replace"]
    value: Any


class PatchOpMove(PatchOpBase):
    op: Literal["move"]
    from_: str = Field(..., alias="from")


class PatchOpCopy(PatchOpBase):
    op: Literal["copy"]
    from_: str = Field(..., alias="from")


class PatchOpTest(PatchOpBase):
    op: Literal["test"]
    value: Any


IRPatchOp = Union[
    PatchOpAdd,
    PatchOpRemove,
    PatchOpReplace,
    PatchOpMove,
    PatchOpCopy,
    PatchOpTest,
]


class IRPatch(StrictBase):
    ops: List[IRPatchOp] = Field(default_factory=list)
    rationale: Optional[str] = None


# ------------------------------------
# Final IR bundle
# ------------------------------------
class CompileMetadataIR(StrictBase):
    ir_version: str = "v3"
    generated_at: str
    warnings: List[str] = Field(default_factory=list)
    autofixes: List[str] = Field(default_factory=list)


class IRBundleV3(StrictBase):
    page: Optional[PageIR] = None
    data: DataStateIR = Field(default_factory=DataStateIR)
    data_model: DataModelIR = Field(default_factory=DataModelIR)
    components: ComponentIR
    tree: ComponentTreeIR
    layout: LayoutIR = Field(default_factory=LayoutIR)
    behavior: BehaviorIR = Field(default_factory=BehaviorIR)
    metadata: CompileMetadataIR


# Backward-compatible schema used by current ir_generation/ir_to_react services.
class IRBundle(StrictBase):
    page_ir: Dict[str, Any] | None = None
    data_ir: Dict[str, Any]
    data_model_ir: Dict[str, Any] = Field(default_factory=dict)
    behaviour_ir: Dict[str, Any]
    component_ir: Dict[str, Any]
    layout_ir: Dict[str, Any]


# # Complex IR Type

# from __future__ import annotations

# from enum import Enum
# from typing import Any, Dict, List, Literal, Optional, Union

# from pydantic import BaseModel, ConfigDict, Field


# # =============================================================================
# # Strict base (no extra fields)
# # =============================================================================
# class StrictBase(BaseModel):
#     model_config = ConfigDict(extra="forbid")


# # =============================================================================
# # Expression AST (safe, typed)
# # =============================================================================
# class ExprNodeKind(str, Enum):
#     literal = "Literal"
#     identifier = "Identifier"
#     binary = "BinaryExpression"
#     logical = "LogicalExpression"
#     conditional = "ConditionalExpression"
#     call = "CallExpression"
#     member = "MemberExpression"
#     array = "ArrayExpression"
#     object = "ObjectExpression"
#     unary = "UnaryExpression"


# class ExpressionNode(StrictBase):
#     kind: ExprNodeKind


# class LiteralNode(ExpressionNode):
#     kind: Literal[ExprNodeKind.literal]
#     value: Union[str, float, int, bool, None]


# class IdentifierNode(ExpressionNode):
#     kind: Literal[ExprNodeKind.identifier]
#     name: str


# class MemberNode(ExpressionNode):
#     kind: Literal[ExprNodeKind.member]
#     object: ExpressionNode
#     property: ExpressionNode


# class UnaryNode(ExpressionNode):
#     kind: Literal[ExprNodeKind.unary]
#     operator: Literal["!", "+", "-", "typeof"]
#     argument: ExpressionNode


# class BinaryNode(ExpressionNode):
#     kind: Literal[ExprNodeKind.binary]
#     operator: Literal[
#         "+",
#         "-",
#         "*",
#         "/",
#         "%",
#         "<",
#         "<=",
#         ">",
#         ">=",
#         "==",
#         "!=",
#         "===",
#         "!==",
#         "in",
#     ]
#     left: ExpressionNode
#     right: ExpressionNode


# class LogicalNode(ExpressionNode):
#     kind: Literal[ExprNodeKind.logical]
#     operator: Literal["&&", "||"]
#     left: ExpressionNode
#     right: ExpressionNode


# class ConditionalNode(ExpressionNode):
#     kind: Literal[ExprNodeKind.conditional]
#     test: ExpressionNode
#     consequent: ExpressionNode
#     alternate: ExpressionNode


# class CallNode(ExpressionNode):
#     kind: Literal[ExprNodeKind.call]
#     callee: ExpressionNode
#     arguments: List[ExpressionNode] = Field(default_factory=list)


# class ArrayNode(ExpressionNode):
#     kind: Literal[ExprNodeKind.array]
#     elements: List[ExpressionNode] = Field(default_factory=list)


# class ObjectProperty(StrictBase):
#     key: Union[str, ExpressionNode]
#     value: ExpressionNode


# class ObjectNode(ExpressionNode):
#     kind: Literal[ExprNodeKind.object]
#     properties: List[ObjectProperty] = Field(default_factory=list)


# ExprAST = Union[
#     LiteralNode,
#     IdentifierNode,
#     MemberNode,
#     UnaryNode,
#     BinaryNode,
#     LogicalNode,
#     ConditionalNode,
#     CallNode,
#     ArrayNode,
#     ObjectNode,
# ]


# # =============================================================================
# # IRValue (literal | expression | template string)
# # =============================================================================
# class TemplateChunk(StrictBase):
#     type: Literal["text", "expr"]
#     text: Optional[str] = None
#     expr: Optional[ExprAST] = None


# class TemplateString(StrictBase):
#     kind: Literal["template"] = "template"
#     chunks: List[TemplateChunk] = Field(default_factory=list)


# class IRLiteral(StrictBase):
#     kind: Literal["literal"] = "literal"
#     value: Any


# class IRExpr(StrictBase):
#     kind: Literal["expr"] = "expr"
#     expr: ExprAST


# IRValue = Union[IRLiteral, IRExpr, TemplateString]


# # =============================================================================
# # Page / App-level policy
# # =============================================================================
# class StyleIR(StrictBase):
#     tone: Optional[str] = None
#     theme: Optional[str] = None
#     density: Optional[str] = None
#     color_intent: Optional[str] = None


# class AccessibilityIR(StrictBase):
#     required_labels: List[str] = Field(default_factory=list)


# class BreakpointsIR(StrictBase):
#     breakpoints: Dict[str, int] = Field(default_factory=dict)


# class ResponsiveRuleIR(StrictBase):
#     rule_id: str
#     when: ExprAST
#     target_node_id: str
#     layout_override: Dict[str, Any] = Field(default_factory=dict)
#     visible_override: Optional[bool] = None


# class PageIR(StrictBase):
#     page_id: str
#     page_goal: Optional[str] = None
#     style: Optional[StyleIR] = None
#     accessibility: Optional[AccessibilityIR] = None
#     breakpoints: Optional[BreakpointsIR] = None
#     responsive_rules: List[ResponsiveRuleIR] = Field(default_factory=list)
#     constraints: List[str] = Field(default_factory=list)


# # =============================================================================
# # App shell / routing / navigation
# # =============================================================================
# class RouteParamIR(StrictBase):
#     name: str
#     type: Literal["string", "number", "boolean"] = "string"
#     required: bool = False


# class RouteIR(StrictBase):
#     route_id: str
#     path: str
#     page_id: str
#     params: List[RouteParamIR] = Field(default_factory=list)
#     title: Optional[str] = None


# class NavItemIR(StrictBase):
#     item_id: str
#     label: str
#     route_id: Optional[str] = None
#     icon: Optional[str] = None
#     children: List[str] = Field(default_factory=list)
#     visible_when: Optional[ExprAST] = None
#     disabled_when: Optional[ExprAST] = None


# class NavGroupIR(StrictBase):
#     group_id: str
#     label: str
#     items: List[str] = Field(default_factory=list)


# class NavIR(StrictBase):
#     groups: Dict[str, NavGroupIR] = Field(default_factory=dict)
#     items: Dict[str, NavItemIR] = Field(default_factory=dict)
#     selected_item_id_bind: Optional[str] = None


# class PermissionsIR(StrictBase):
#     notes: Optional[str] = None


# class AppIR(StrictBase):
#     active_route_id_bind: Optional[str] = None
#     routes: Dict[str, RouteIR] = Field(default_factory=dict)
#     nav: Optional[NavIR] = None
#     permissions: Optional[PermissionsIR] = None
#     feature_flags: Dict[str, bool] = Field(default_factory=dict)


# # =============================================================================
# # Data state + derived + schema/model
# # =============================================================================
# DataType = Literal["number", "string", "boolean", "array", "object", "enum", "date", "null"]


# class StateField(StrictBase):
#     type: DataType
#     initial: Any
#     required: bool = False
#     constraints: Dict[str, Any] = Field(default_factory=dict)
#     description: Optional[str] = None


# class DerivedField(StrictBase):
#     type: DataType
#     expr: ExprAST
#     description: Optional[str] = None


# class DataStateIR(StrictBase):
#     state: Dict[str, StateField] = Field(default_factory=dict)
#     derived: Dict[str, DerivedField] = Field(default_factory=dict)


# class EntityFieldIR(StrictBase):
#     name: str
#     type: DataType
#     description: Optional[str] = None


# class EntityIR(StrictBase):
#     name: str
#     fields: List[EntityFieldIR] = Field(default_factory=list)
#     computed: List[str] = Field(default_factory=list)
#     display_fields: List[str] = Field(default_factory=list)
#     filters: List[Dict[str, Any]] = Field(default_factory=list)
#     sort_by: Optional[str] = None
#     pagination: Optional[bool] = None


# class DataModelIR(StrictBase):
#     entities: Dict[str, EntityIR] = Field(default_factory=dict)


# # =============================================================================
# # Data sources (async)
# # =============================================================================
# class DataSourceKind(str, Enum):
#     rest = "rest"
#     graphql = "graphql"
#     sql = "sql"
#     rpc = "rpc"


# class DataSourceTrigger(str, Enum):
#     page_load = "page_load"
#     manual = "manual"
#     interval = "interval"
#     state_change = "state_change"


# class DataSourceRequestIR(StrictBase):
#     method: Optional[Literal["GET", "POST", "PUT", "PATCH", "DELETE"]] = None
#     endpoint: Optional[str] = None
#     query: Optional[str] = None
#     operation_name: Optional[str] = None
#     sql: Optional[str] = None
#     procedure: Optional[str] = None
#     params: Dict[str, IRValue] = Field(default_factory=dict)
#     headers: Dict[str, IRValue] = Field(default_factory=dict)
#     body: Optional[IRValue] = None


# class DataSourceIR(StrictBase):
#     source_id: str
#     kind: DataSourceKind
#     trigger: DataSourceTrigger = DataSourceTrigger.manual
#     request: DataSourceRequestIR
#     result_bind: str
#     loading_bind: Optional[str] = None
#     error_bind: Optional[str] = None
#     interval_ms: Optional[int] = None
#     watch: List[str] = Field(default_factory=list)


# class DataSourcesIR(StrictBase):
#     sources: Dict[str, DataSourceIR] = Field(default_factory=dict)


# # =============================================================================
# # Component library
# # =============================================================================
# class CSSValueType(str, Enum):
#     px = "px"
#     em = "em"
#     rem = "rem"
#     percent = "%"
#     color = "color"
#     keyword = "keyword"


# class CSSValue(StrictBase):
#     value: Union[int, float, str]
#     unit: Optional[CSSValueType] = None


# class ThemeConfig(StrictBase):
#     primaryColor: Optional[str] = None
#     secondaryColor: Optional[str] = None
#     fontFamily: Optional[str] = None
#     borderRadius: Optional[int] = None


# class ComponentDefinition(StrictBase):
#     type: str
#     label: Optional[str] = None
#     bind: Optional[str] = None
#     onClick: Optional[str] = None
#     props: Dict[str, IRValue] = Field(default_factory=dict)
#     styles: Dict[str, Union[CSSValue, IRValue]] = Field(default_factory=dict)
#     a11y_labels: List[str] = Field(default_factory=list)


# class ComponentIR(StrictBase):
#     library: Literal["antd"] = "antd"
#     theme: Optional[ThemeConfig] = None
#     components: Dict[str, ComponentDefinition] = Field(default_factory=dict)


# # =============================================================================
# # Tree semantics (repeat / condition / slots)
# # =============================================================================
# class RepeatIR(StrictBase):
#     items: ExprAST
#     as_: str = "item"
#     index_as: Optional[str] = "index"
#     key: Optional[ExprAST] = None
#     empty_state_node_id: Optional[str] = None
#     loading_node_id: Optional[str] = None


# class NodeEventBinding(StrictBase):
#     event: str
#     action_id: str


# class ComponentNodeIR(StrictBase):
#     node_id: str
#     component_id: str
#     parent_id: Optional[str] = None
#     children: List[str] = Field(default_factory=list)
#     slots: Dict[str, List[str]] = Field(default_factory=dict)
#     repeat: Optional[RepeatIR] = None
#     visible_when: Optional[ExprAST] = None
#     disabled_when: Optional[ExprAST] = None
#     props: Dict[str, IRValue] = Field(default_factory=dict)
#     styles: Dict[str, Union[CSSValue, IRValue]] = Field(default_factory=dict)
#     zone_id: Optional[str] = None
#     kind: Optional[str] = None
#     events: List[NodeEventBinding] = Field(default_factory=list)


# class ComponentTreeIR(StrictBase):
#     root_id: str = "root"
#     nodes: Dict[str, ComponentNodeIR] = Field(default_factory=dict)


# # =============================================================================
# # Layout
# # =============================================================================
# class LayoutType(str, Enum):
#     vertical = "vertical"
#     horizontal = "horizontal"
#     grid = "grid"
#     wrap = "wrap"
#     absolute = "absolute"


# class LayoutConfig(StrictBase):
#     type: LayoutType
#     gap: Optional[int] = None
#     columns: Optional[int] = None
#     rowGap: Optional[int] = None
#     colGap: Optional[int] = None
#     align: Optional[Literal["start", "center", "end", "stretch"]] = None
#     justify: Optional[
#         Literal["start", "center", "end", "between", "around", "evenly"]
#     ] = None


# class PlacementIR(StrictBase):
#     strategy: Literal["anchor", "overlay", "auto_flow"] = "auto_flow"
#     justify: Literal["start", "center", "end", "stretch"] = "start"
#     align: Literal["start", "center", "end", "stretch"] = "start"
#     width: Optional[str] = None
#     height: Optional[str] = None
#     z_index_token: Optional[str] = None


# class LayoutZoneIR(StrictBase):
#     zone_id: str
#     node_id: str
#     anchor: Optional[str] = None
#     size_hint: Optional[str] = None
#     z_layer: Literal["base", "overlay"] = "base"
#     placement: PlacementIR = Field(default_factory=PlacementIR)
#     notes: Optional[str] = None


# class LayoutIR(StrictBase):
#     strategy: Literal["desktop-first", "mobile-first", "adaptive"] = "desktop-first"
#     breakpoints: Dict[str, int] = Field(default_factory=dict)
#     layout: Dict[str, LayoutConfig] = Field(default_factory=dict)
#     zones: Dict[str, LayoutZoneIR] = Field(default_factory=dict)


# # =============================================================================
# # Overlays
# # =============================================================================
# class OverlayKind(str, Enum):
#     modal = "modal"
#     drawer = "drawer"
#     popover = "popover"
#     tooltip = "tooltip"


# class OverlayIR(StrictBase):
#     overlay_id: str
#     kind: OverlayKind
#     content_root_node_id: str
#     open_when: Optional[ExprAST] = None
#     on_close_action_id: Optional[str] = None
#     props: Dict[str, IRValue] = Field(default_factory=dict)


# class OverlaysIR(StrictBase):
#     overlays: Dict[str, OverlayIR] = Field(default_factory=dict)


# # =============================================================================
# # Collections
# # =============================================================================
# class SortDir(str, Enum):
#     asc = "asc"
#     desc = "desc"


# class CollectionPagingIR(StrictBase):
#     page_bind: str
#     page_size_bind: str
#     total_bind: Optional[str] = None


# class CollectionIR(StrictBase):
#     collection_id: str
#     items_expr: ExprAST
#     filters_expr: Optional[ExprAST] = None
#     sort_expr: Optional[ExprAST] = None
#     paging: Optional[CollectionPagingIR] = None
#     refresh_source_id: Optional[str] = None


# class CollectionsIR(StrictBase):
#     collections: Dict[str, CollectionIR] = Field(default_factory=dict)


# # =============================================================================
# # Forms
# # =============================================================================
# class ValidatorIR(StrictBase):
#     message: str
#     expr: ExprAST


# class FormFieldIR(StrictBase):
#     field_id: str
#     bind: str
#     type: DataType
#     label: Optional[str] = None
#     required: bool = False
#     validators: List[ValidatorIR] = Field(default_factory=list)
#     normalize: Optional[ExprAST] = None


# class FormIR(StrictBase):
#     form_id: str
#     fields: Dict[str, FormFieldIR] = Field(default_factory=dict)
#     submit_action_id: Optional[str] = None
#     reset_action_id: Optional[str] = None


# class FormsIR(StrictBase):
#     forms: Dict[str, FormIR] = Field(default_factory=dict)


# # =============================================================================
# # Behavior
# # =============================================================================
# class MutationUpdate(StrictBase):
#     target: str
#     expr: ExprAST


# class EffectType(str, Enum):
#     mutation = "mutation"
#     navigate = "navigate"
#     open_overlay = "open_overlay"
#     close_overlay = "close_overlay"
#     run_data_source = "run_data_source"
#     notify = "notify"


# class NavigatePayload(StrictBase):
#     route_id: str
#     params: Dict[str, IRValue] = Field(default_factory=dict)
#     replace: bool = False


# class OverlayPayload(StrictBase):
#     overlay_id: str


# class RunDataSourcePayload(StrictBase):
#     source_id: str
#     params: Dict[str, IRValue] = Field(default_factory=dict)
#     body: Optional[IRValue] = None


# class NotifyPayload(StrictBase):
#     level: Literal["info", "success", "warning", "error"] = "info"
#     message: IRValue
#     description: Optional[IRValue] = None
#     duration_sec: Optional[int] = None


# class ActionEffect(StrictBase):
#     type: EffectType
#     mutation_updates: List[MutationUpdate] = Field(default_factory=list)
#     navigate: Optional[NavigatePayload] = None
#     overlay: Optional[OverlayPayload] = None
#     run_data_source: Optional[RunDataSourcePayload] = None
#     notify: Optional[NotifyPayload] = None


# class ActionDefinition(StrictBase):
#     action_id: str
#     label: Optional[str] = None
#     preconditions: List[ExprAST] = Field(default_factory=list)
#     effects: List[ActionEffect] = Field(default_factory=list)
#     requires_confirmation: bool = False
#     confirmation_message: Optional[IRValue] = None


# class FeedbackDefinition(StrictBase):
#     action_id: str
#     loading: Optional[IRValue] = None
#     success: Optional[IRValue] = None
#     error: Optional[IRValue] = None
#     messages: List[IRValue] = Field(default_factory=list)


# class BehaviorIR(StrictBase):
#     actions: Dict[str, ActionDefinition] = Field(default_factory=dict)
#     feedback: Dict[str, FeedbackDefinition] = Field(default_factory=dict)
#     constraints: List[ExprAST] = Field(default_factory=list)


# # =============================================================================
# # Patch ops
# # =============================================================================
# class PatchOpBase(StrictBase):
#     op: Literal["add", "remove", "replace", "move", "copy", "test"]
#     path: str


# class PatchOpAdd(PatchOpBase):
#     op: Literal["add"]
#     value: Any


# class PatchOpRemove(PatchOpBase):
#     op: Literal["remove"]


# class PatchOpReplace(PatchOpBase):
#     op: Literal["replace"]
#     value: Any


# class PatchOpMove(PatchOpBase):
#     op: Literal["move"]
#     from_: str = Field(..., alias="from")


# class PatchOpCopy(PatchOpBase):
#     op: Literal["copy"]
#     from_: str = Field(..., alias="from")


# class PatchOpTest(PatchOpBase):
#     op: Literal["test"]
#     value: Any


# IRPatchOp = Union[
#     PatchOpAdd,
#     PatchOpRemove,
#     PatchOpReplace,
#     PatchOpMove,
#     PatchOpCopy,
#     PatchOpTest,
# ]


# class IRPatch(StrictBase):
#     ops: List[IRPatchOp] = Field(default_factory=list)
#     rationale: Optional[str] = None


# # =============================================================================
# # Metadata + Final Bundle
# # =============================================================================
# class CompileMetadataIR(StrictBase):
#     ir_version: str = "v4"
#     generated_at: str
#     warnings: List[str] = Field(default_factory=list)
#     autofixes: List[str] = Field(default_factory=list)


# class IRBundleV4(StrictBase):
#     app: Optional[AppIR] = None
#     page: PageIR
#     data: DataStateIR = Field(default_factory=DataStateIR)
#     data_model: DataModelIR = Field(default_factory=DataModelIR)
#     data_sources: DataSourcesIR = Field(default_factory=DataSourcesIR)
#     components: ComponentIR
#     tree: ComponentTreeIR
#     layout: LayoutIR = Field(default_factory=LayoutIR)
#     overlays: OverlaysIR = Field(default_factory=OverlaysIR)
#     collections: CollectionsIR = Field(default_factory=CollectionsIR)
#     forms: FormsIR = Field(default_factory=FormsIR)
#     behavior: BehaviorIR = Field(default_factory=BehaviorIR)
#     metadata: CompileMetadataIR


# # Backward import name used across services.
# IRBundle = IRBundleV4
