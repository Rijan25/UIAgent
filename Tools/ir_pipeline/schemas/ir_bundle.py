"""IR bundle schema v3.5.

Complete template for broad UI scenarios while keeping compatibility with the
existing generation pipeline.
"""

from __future__ import annotations

from typing import Any, Dict, List, Literal, Optional, Union

from pydantic import BaseModel, ConfigDict, Field


class StrictBase(BaseModel):
    model_config = ConfigDict(extra="forbid")


# ============================================================================
# 1. PAGE IR
# ============================================================================


class StyleConfig(StrictBase):
    tone: Optional[str] = None
    theme: Optional[str] = None
    density: Optional[Literal["compact", "comfortable", "spacious"]] = None
    color_intent: Optional[str] = None


class ResponsiveConfig(StrictBase):
    breakpoints: Dict[str, int] = Field(
        default_factory=lambda: {"sm": 640, "md": 768, "lg": 1024, "xl": 1280}
    )
    collapse_rules: List[str] = Field(default_factory=list)
    hidden_on_small: List[str] = Field(default_factory=list)
    stack_on_small: List[str] = Field(default_factory=list)


class AccessibilityConfig(StrictBase):
    required_labels: List[str] = Field(default_factory=list)
    skip_navigation: bool = True
    focus_management: bool = True
    announce_changes: List[str] = Field(default_factory=list)


class PageIR(StrictBase):
    page_id: str = ""
    page_goal: str = ""
    style: StyleConfig = Field(default_factory=StyleConfig)
    accessibility: AccessibilityConfig = Field(default_factory=AccessibilityConfig)
    responsive: ResponsiveConfig = Field(default_factory=ResponsiveConfig)
    constraints: List[str] = Field(default_factory=list)
    seo_title: Optional[str] = None
    seo_description: Optional[str] = None


# ============================================================================
# 2. DATA IR
# ============================================================================


class TypeFieldDef(StrictBase):
    type: str
    required: bool = True
    enum_values: Optional[List[str]] = None
    item_type: Optional[str] = None
    ref_type: Optional[str] = None
    format: Optional[str] = None


class CustomTypeDef(StrictBase):
    name: str
    fields: Dict[str, TypeFieldDef] = Field(default_factory=dict)
    description: str = ""


class StateFieldDef(StrictBase):
    type: str
    initial: Any = None
    required: bool = False
    constraints: Dict[str, Any] = Field(default_factory=dict)
    item_type: Optional[str] = None


class DerivedFieldDef(StrictBase):
    type: str
    expr: str
    deps: List[str] = Field(default_factory=list)


class DataIR(StrictBase):
    types: Dict[str, CustomTypeDef] = Field(default_factory=dict)
    state: Dict[str, StateFieldDef] = Field(default_factory=dict)
    derived: Dict[str, DerivedFieldDef] = Field(default_factory=dict)


# ============================================================================
# 3. DATA FETCH IR
# ============================================================================


class DataEndpointDef(StrictBase):
    endpoint_id: str
    form_id: Optional[int] = None
    endpoint: str = "/api/data/query"
    method: Literal["GET", "POST", "PUT", "PATCH", "DELETE"] = "POST"
    fields: List[str] = Field(default_factory=list)
    filters: List[Dict[str, Any]] = Field(default_factory=list)
    aggregation: Optional[str] = None
    group_by: Optional[str] = None
    sort: Optional[Dict[str, str]] = None
    page_size: Optional[int] = None

    response_target: str
    response_transform: Optional[str] = None

    trigger: Literal["on_mount", "on_change", "manual"] = "on_mount"
    depends_on: List[str] = Field(default_factory=list)
    debounce_ms: Optional[int] = None

    loading_field: Optional[str] = None
    error_field: Optional[str] = None


class DataFetchIR(StrictBase):
    endpoints: Dict[str, DataEndpointDef] = Field(default_factory=dict)


# ============================================================================
# 4. DATA MODEL IR
# ============================================================================


class EntityFieldDef(StrictBase):
    name: str
    type: str
    label: Optional[str] = None
    encoded_key: Optional[str] = None
    is_primary: bool = False
    is_reference: bool = False
    reference_to: Optional[str] = None
    enum_values: Optional[List[str]] = None
    format: Optional[str] = None


class EntityDef(StrictBase):
    name: str
    fields: List[Union[str, EntityFieldDef]] = Field(default_factory=list)
    computed: List[str] = Field(default_factory=list)
    display_fields: List[str] = Field(default_factory=list)
    search_fields: List[str] = Field(default_factory=list)
    filters: List[str] = Field(default_factory=list)
    default_sort: Optional[str] = None
    default_sort_dir: str = "asc"


class RelationshipDef(StrictBase):
    from_entity: str
    from_field: str
    to_entity: str
    to_field: str = "id"
    type: Literal["one_to_one", "one_to_many", "many_to_one", "many_to_many"] = "many_to_one"


class DataModelIR(StrictBase):
    entities: Dict[str, EntityDef] = Field(default_factory=dict)
    relationships: List[RelationshipDef] = Field(default_factory=list)

    # Optional extension used by the current SQL-driven workflow.
    external_source_ref: Optional[Dict[str, Any]] = None
    sql_query_ir: Optional[Dict[str, Any]] = None


# ============================================================================
# 5. BEHAVIOUR IR
# ============================================================================


class MutationUpdateDef(StrictBase):
    target: str
    expr: str


class EventDef(StrictBase):
    type: Literal["mutation", "api_call", "navigation", "custom"] = "mutation"
    updates: List[MutationUpdateDef] = Field(default_factory=list)
    description: str = ""


class SideEffectDef(StrictBase):
    type: Literal[
        "toast",
        "navigate",
        "refresh",
        "modal_open",
        "modal_close",
        "drawer_open",
        "drawer_close",
        "download",
        "clipboard",
        "reset_state",
        "api_call",
        "custom",
    ]
    config: Dict[str, Any] = Field(default_factory=dict)


class ActionDef(StrictBase):
    action_id: str
    trigger: str
    target_component_id: Optional[str] = None
    operation: Literal["create", "update", "delete", "read", "custom"] = "custom"
    description: str = ""

    payload: Dict[str, Any] = Field(default_factory=dict)
    guard: Optional[str] = None

    requires_confirmation: bool = False
    confirmation_message: Optional[str] = None

    validation_rules: List[str] = Field(default_factory=list)
    validation_messages: Dict[str, str] = Field(default_factory=dict)

    updates: List[MutationUpdateDef] = Field(default_factory=list)

    api_endpoint: Optional[str] = None
    api_body: Optional[str] = None

    side_effects: List[SideEffectDef] = Field(default_factory=list)

    then: Optional[str] = None
    catch: Optional[str] = None


class FeedbackDef(StrictBase):
    action_id: str
    loading_indicator: Optional[str] = None
    loading_text: Optional[str] = None
    success_message: Optional[str] = None
    error_message: Optional[str] = None
    ui_updates: List[str] = Field(default_factory=list)


class BehaviourIR(StrictBase):
    events: Dict[str, EventDef] = Field(default_factory=dict)
    actions: Dict[str, ActionDef] = Field(default_factory=dict)
    feedback: Dict[str, FeedbackDef] = Field(default_factory=dict)


# ============================================================================
# 6. COMPONENT IR
# ============================================================================


class RepeatDef(StrictBase):
    source: str
    item_alias: str
    index_alias: str = "index"
    key_expr: str
    empty_text: Optional[str] = None
    empty_component: Optional[str] = None


class TransitionDef(StrictBase):
    property: str = "all"
    duration: str = "0.2s"
    easing: str = "ease"
    trigger: str = "state_change"


class ComponentDef(StrictBase):
    type: str
    label: Optional[str] = None
    description: Optional[str] = None

    bind: Optional[str] = None

    onClick: Optional[str] = None
    onChange: Optional[str] = None
    onSubmit: Optional[str] = None
    onHover: Optional[str] = None
    onKeyPress: Optional[Dict[str, str]] = None

    props: Dict[str, Any] = Field(default_factory=dict)
    dynamic_props: Dict[str, str] = Field(default_factory=dict)

    styles: Dict[str, Any] = Field(default_factory=dict)
    dynamic_styles: Dict[str, str] = Field(default_factory=dict)

    class_name: Optional[str] = None
    dynamic_class: Optional[str] = None

    transitions: List[TransitionDef] = Field(default_factory=list)

    visible_when: Optional[str] = None
    disabled_when: Optional[str] = None

    repeat: Optional[RepeatDef] = None

    slots: Dict[str, str] = Field(default_factory=dict)

    a11y_role: Optional[str] = None
    a11y_label: Optional[str] = None


class ThemeConfig(StrictBase):
    primaryColor: Optional[str] = None
    secondaryColor: Optional[str] = None
    successColor: Optional[str] = None
    warningColor: Optional[str] = None
    errorColor: Optional[str] = None
    fontFamily: Optional[str] = None
    fontSize: Optional[int] = None
    borderRadius: Optional[int] = None


class ComponentIR(StrictBase):
    library: Literal["antd", "custom", "hybrid"] = "antd"
    theme: ThemeConfig = Field(default_factory=ThemeConfig)
    components: Dict[str, ComponentDef] = Field(default_factory=dict)


# ============================================================================
# 7. LAYOUT IR
# ============================================================================


class LayoutDef(StrictBase):
    type: Literal["vertical", "horizontal", "grid", "sidebar", "stack"] = "vertical"
    gap: Optional[int] = None
    padding: Optional[str] = None
    columns: Optional[int] = None
    column_template: Optional[str] = None
    row_template: Optional[str] = None
    align_items: Optional[str] = None
    justify_content: Optional[str] = None
    wrap: bool = False
    min_height: Optional[str] = None
    overflow: Optional[str] = None


class LayoutZoneDef(StrictBase):
    zone_id: str
    component: str
    anchor: str = "center"
    size_hint: str = "auto"
    z_layer: Literal["base", "overlay", "modal", "toast"] = "base"
    notes: str = ""


class ResponsiveOverride(StrictBase):
    breakpoint: str
    layout_overrides: Dict[str, LayoutDef] = Field(default_factory=dict)
    hidden_components: List[str] = Field(default_factory=list)
    visibility_overrides: Dict[str, str] = Field(default_factory=dict)


class LayoutIR(StrictBase):
    root: str = ""
    children: Dict[str, List[str]] = Field(default_factory=dict)
    layout: Dict[str, LayoutDef] = Field(default_factory=dict)
    layout_zones: List[LayoutZoneDef] = Field(default_factory=list)
    responsive_overrides: List[ResponsiveOverride] = Field(default_factory=list)


# ============================================================================
# 8. NAVIGATION IR
# ============================================================================


class TabDef(StrictBase):
    tab_id: str
    label: str
    icon: Optional[str] = None
    content_root: str
    badge_expr: Optional[str] = None
    disabled_when: Optional[str] = None
    default: bool = False


class ModalDef(StrictBase):
    modal_id: str
    title: str
    title_expr: Optional[str] = None
    width: Optional[int] = None
    trigger_state: str
    content_root: str
    on_close_event: Optional[str] = None
    closable: bool = True
    mask_closable: bool = True
    footer_actions: List[str] = Field(default_factory=list)


class DrawerDef(StrictBase):
    drawer_id: str
    title: str
    title_expr: Optional[str] = None
    width: str = "400px"
    placement: Literal["left", "right", "top", "bottom"] = "right"
    trigger_state: str
    content_root: str
    on_close_event: Optional[str] = None
    closable: bool = True


class RouteDef(StrictBase):
    path: str
    page_id: str
    label: str = ""
    icon: Optional[str] = None
    guard: Optional[str] = None
    params: List[str] = Field(default_factory=list)


class BreadcrumbDef(StrictBase):
    items: List[Dict[str, str]] = Field(default_factory=list)


class NavigationIR(StrictBase):
    tabs: List[TabDef] = Field(default_factory=list)
    modals: Dict[str, ModalDef] = Field(default_factory=dict)
    drawers: Dict[str, DrawerDef] = Field(default_factory=dict)
    routes: List[RouteDef] = Field(default_factory=list)
    breadcrumb: Optional[BreadcrumbDef] = None
    default_tab: Optional[str] = None


# ============================================================================
# 9. REALTIME IR
# ============================================================================


class TimerDef(StrictBase):
    timer_id: str
    type: Literal["interval", "timeout", "countdown"] = "interval"
    interval_ms: int = 1000
    action: str
    auto_start: bool = True
    stop_when: Optional[str] = None
    description: str = ""


class PollingDef(StrictBase):
    polling_id: str
    endpoint_id: str
    interval_ms: int = 30000
    active_when: Optional[str] = None
    description: str = ""


class RealtimeIR(StrictBase):
    timers: Dict[str, TimerDef] = Field(default_factory=dict)
    polling: Dict[str, PollingDef] = Field(default_factory=dict)


# ============================================================================
# 10. METADATA
# ============================================================================


class MetadataIR(StrictBase):
    ir_version: str = "3.5"
    generated_at: str = ""
    source_prompt: Optional[str] = None
    schema_session_id: Optional[str] = None
    warnings: List[str] = Field(default_factory=list)


# ============================================================================
# FINAL BUNDLE
# ============================================================================


class IRBundle(StrictBase):
    page_ir: PageIR = Field(default_factory=PageIR)
    data_ir: DataIR = Field(default_factory=DataIR)
    data_fetch_ir: DataFetchIR = Field(default_factory=DataFetchIR)
    data_model_ir: DataModelIR = Field(default_factory=DataModelIR)
    behaviour_ir: BehaviourIR = Field(default_factory=BehaviourIR)
    component_ir: ComponentIR = Field(default_factory=ComponentIR)
    layout_ir: LayoutIR = Field(default_factory=LayoutIR)
    navigation_ir: NavigationIR = Field(default_factory=NavigationIR)
    realtime_ir: RealtimeIR = Field(default_factory=RealtimeIR)
    metadata: MetadataIR = Field(default_factory=MetadataIR)
