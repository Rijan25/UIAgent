"""

Complete IR template covering ALL UI scenarios.
Uses simple string expressions (not nested ExprAST).
AI reads this template → generates valid IR for any user request.

Covers:
  1. State + Derived (with string expressions)
  2. Custom Types
  3. Data Fetching (runtime API calls, loading/error states)
  4. Entities + Relationships
  5. Components (Ant Design, with dynamic props/styles/conditional/repeat)
  6. Layout (vertical, horizontal, grid, sidebar, stack)
  7. Behavior (events, actions, validation, side effects, chaining, guards)
  8. Navigation (tabs, modals, drawers, breadcrumbs, routes)
  9. Real-time (timers, polling)
  10. Page-level (style, accessibility, responsive, constraints)

Design:
  - Expressions are PLAIN STRINGS: "state.items.filter(x => x.active)"
  - No nested AST nodes
  - Flat JSON structure
  - AI generates this reliably (~95% first attempt)
  - Code generator reads this → picks Ant Design components → assembles React
"""

from __future__ import annotations
from pydantic import BaseModel, Field, ConfigDict
from typing import Any, Dict, List, Literal, Optional, Union
from enum import Enum


class StrictBase(BaseModel):
    model_config = ConfigDict(extra="forbid")


# ============================================================================
# 1. PAGE IR — Page-level metadata, style, accessibility
# ============================================================================

class StyleConfig(StrictBase):
    tone: Optional[str] = None                    # "professional", "playful", "minimal"
    theme: Optional[str] = None                   # "light", "dark"
    density: Optional[Literal["compact", "comfortable", "spacious"]] = None
    color_intent: Optional[str] = None            # "primary", "warehouse-industrial"

class ResponsiveConfig(StrictBase):
    breakpoints: Dict[str, int] = Field(default_factory=lambda: {
        "sm": 640, "md": 768, "lg": 1024, "xl": 1280
    })
    collapse_rules: List[str] = Field(default_factory=list)       # ["sidebar_to_drawer_on_sm"]
    hidden_on_small: List[str] = Field(default_factory=list)      # component_ids to hide on mobile
    stack_on_small: List[str] = Field(default_factory=list)       # horizontal → vertical on mobile

class AccessibilityConfig(StrictBase):
    required_labels: List[str] = Field(default_factory=list)
    skip_navigation: bool = True
    focus_management: bool = True
    announce_changes: List[str] = Field(default_factory=list)     # state fields to announce

class PageIR(StrictBase):
    page_id: str = ""
    page_goal: str = ""
    style: StyleConfig = Field(default_factory=StyleConfig)
    accessibility: AccessibilityConfig = Field(default_factory=AccessibilityConfig)
    responsive: ResponsiveConfig = Field(default_factory=ResponsiveConfig)
    constraints: List[str] = Field(default_factory=list)          # ["fullscreen_layout", "no_scroll"]
    seo_title: Optional[str] = None
    seo_description: Optional[str] = None


# ============================================================================
# 2. DATA IR — State, Derived, Custom Types
# ============================================================================

class TypeFieldDef(StrictBase):
    """Field definition within a custom type."""
    type: str                                    # "string", "number", "boolean", "date", "array", "object", "enum"
    required: bool = True
    enum_values: Optional[List[str]] = None      # for enum type
    item_type: Optional[str] = None              # for array: type of items
    ref_type: Optional[str] = None               # for object: reference to another type
    format: Optional[str] = None                 # "currency", "date", "percent", "duration"

class CustomTypeDef(StrictBase):
    """Custom type definition — becomes TypeScript interface."""
    name: str
    fields: Dict[str, TypeFieldDef] = Field(default_factory=dict)
    description: str = ""

class StateFieldDef(StrictBase):
    """A piece of reactive state — becomes useState in React."""
    type: str                                    # "string", "number", "boolean", "array", "object"
    initial: Any = None
    required: bool = False
    constraints: Dict[str, Any] = Field(default_factory=dict)    # {"min": 0, "max": 100, "maxLength": 50}
    item_type: Optional[str] = None              # for arrays: type name

class DerivedFieldDef(StrictBase):
    """Computed value — becomes useMemo in React. Expression is a plain string."""
    type: str
    expr: str                                    # "state.items.filter(x => x.active)"
    deps: List[str] = Field(default_factory=list)  # ["state.items", "state.filterTerm"]

class DataIR(StrictBase):
    types: Dict[str, CustomTypeDef] = Field(default_factory=dict)
    state: Dict[str, StateFieldDef] = Field(default_factory=dict)
    derived: Dict[str, DerivedFieldDef] = Field(default_factory=dict)


# ============================================================================
# 3. DATA FETCH IR — Runtime API calls
# ============================================================================

class DataEndpointDef(StrictBase):
    """An API call that happens at runtime — component fetches data from DB."""
    endpoint_id: str
    form_id: Optional[int] = None                # Dalfin form ID
    endpoint: str = "/api/data/query"
    method: Literal["GET", "POST", "PUT", "PATCH", "DELETE"] = "POST"
    fields: List[str] = Field(default_factory=list)              # encoded keys: ["k_name_k", "k_sal_k"]
    filters: List[Dict[str, Any]] = Field(default_factory=list)  # [{"field": "k_dept_k", "op": "equals", "value": "$state.filterDept"}]
    aggregation: Optional[str] = None            # "COUNT", "SUM", "AVG", "MIN", "MAX"
    group_by: Optional[str] = None               # "k_dept_k"
    sort: Optional[Dict[str, str]] = None        # {"field": "k_date_k", "dir": "desc"}
    page_size: Optional[int] = None
    
    # Response mapping
    response_target: str                         # state field to store response: "purchaseOrders"
    response_transform: Optional[str] = None     # "response.data.map(r => ({...r, total: r.qty * r.price}))"
    
    # Trigger behavior
    trigger: Literal["on_mount", "on_change", "manual"] = "on_mount"
    depends_on: List[str] = Field(default_factory=list)  # re-fetch when these change: ["state.filterDept"]
    debounce_ms: Optional[int] = None
    
    # Loading/error state
    loading_field: Optional[str] = None          # "loadingOrders"
    error_field: Optional[str] = None            # "ordersError"

class DataFetchIR(StrictBase):
    endpoints: Dict[str, DataEndpointDef] = Field(default_factory=dict)


# ============================================================================
# 4. DATA MODEL IR — Entities, Relationships
# ============================================================================

class EntityFieldDef(StrictBase):
    name: str
    type: str
    label: Optional[str] = None
    encoded_key: Optional[str] = None            # Dalfin encoded column: "k_sal001_k"
    is_primary: bool = False
    is_reference: bool = False
    reference_to: Optional[str] = None           # other entity name
    enum_values: Optional[List[str]] = None
    format: Optional[str] = None                 # "currency", "date", "percent"

class EntityDef(StrictBase):
    name: str
    fields: List[Union[str, EntityFieldDef]] = Field(default_factory=list)   # simple: ["id", "name"] or detailed
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


# ============================================================================
# 5. BEHAVIOUR IR — Events, Actions, Validation, Side Effects
# ============================================================================

class MutationUpdateDef(StrictBase):
    target: str                                  # "state.searchTerm"
    expr: str                                    # "event.target.value"

class EventDef(StrictBase):
    """Simple event handler — usually triggered by component interaction."""
    type: Literal["mutation", "api_call", "navigation", "custom"] = "mutation"
    updates: List[MutationUpdateDef] = Field(default_factory=list)
    description: str = ""

class SideEffectDef(StrictBase):
    """Side effect after an action completes."""
    type: Literal[
        "toast", "navigate", "refresh", "modal_open", "modal_close",
        "drawer_open", "drawer_close", "download", "clipboard",
        "reset_state", "api_call", "custom"
    ]
    config: Dict[str, Any] = Field(default_factory=dict)
    # Examples:
    #   {"type": "toast", "config": {"message": "Saved!", "type": "success"}}
    #   {"type": "navigate", "config": {"path": "/orders"}}
    #   {"type": "refresh", "config": {"endpoint_id": "fetchOrders"}}
    #   {"type": "modal_close", "config": {"modal_id": "addOrderModal"}}
    #   {"type": "reset_state", "config": {"fields": ["newOrder"]}}

class ActionDef(StrictBase):
    """Complex action — triggered by button click, form submit, etc."""
    action_id: str
    trigger: str                                 # "button_click", "form_submit", "input_change", "row_click", "drag_drop"
    target_component_id: Optional[str] = None
    operation: Literal["create", "update", "delete", "read", "custom"] = "custom"
    description: str = ""
    
    # Payload
    payload: Dict[str, Any] = Field(default_factory=dict)
    
    # Guard — only execute if this is true
    guard: Optional[str] = None                  # "state.user.role === 'admin'"
    
    # Confirmation
    requires_confirmation: bool = False
    confirmation_message: Optional[str] = None   # "Are you sure you want to delete?"
    
    # Validation — all must be true before executing
    validation_rules: List[str] = Field(default_factory=list)   # ["state.name !== ''", "state.email.includes('@')"]
    validation_messages: Dict[str, str] = Field(default_factory=dict)  # {"state.name !== ''": "Name is required"}
    
    # State mutations
    updates: List[MutationUpdateDef] = Field(default_factory=list)
    
    # API call (if this action calls an API)
    api_endpoint: Optional[str] = None           # endpoint_id from data_fetch_ir
    api_body: Optional[str] = None               # expression: "{ name: state.newName, id: state.selectedId }"
    
    # Side effects (run after success)
    side_effects: List[SideEffectDef] = Field(default_factory=list)
    
    # Chaining
    then: Optional[str] = None                   # action_id to run after success
    catch: Optional[str] = None                  # action_id to run on failure

class FeedbackDef(StrictBase):
    action_id: str
    loading_indicator: Optional[str] = None      # "spinner", "skeleton", "progress"
    loading_text: Optional[str] = None
    success_message: Optional[str] = None
    error_message: Optional[str] = None
    ui_updates: List[str] = Field(default_factory=list)

class BehaviourIR(StrictBase):
    events: Dict[str, EventDef] = Field(default_factory=dict)
    actions: Dict[str, ActionDef] = Field(default_factory=dict)
    feedback: Dict[str, FeedbackDef] = Field(default_factory=dict)


# ============================================================================
# 6. COMPONENT IR — Ant Design components with full dynamic support
# ============================================================================

class RepeatDef(StrictBase):
    """Render this component for each item in a collection."""
    source: str                                  # "derived.filteredDoors"
    item_alias: str                              # "door"
    index_alias: str = "index"
    key_expr: str                                # "door.id"
    empty_text: Optional[str] = None             # "No items found"
    empty_component: Optional[str] = None        # component_id for custom empty state

class TransitionDef(StrictBase):
    property: str = "all"
    duration: str = "0.2s"
    easing: str = "ease"
    trigger: str = "state_change"                # "hover", "state_change", "mount", "focus"

class ComponentDef(StrictBase):
    """A single UI component definition."""
    type: str                                    # Ant Design: "Table", "Button", "Input", "Select", "Modal", "Form", "Card", etc.
    label: Optional[str] = None
    description: Optional[str] = None
    
    # Data binding
    bind: Optional[str] = None                   # "state.searchTerm", "derived.filteredOrders"
    
    # Event handlers (reference event/action names from behaviour_ir)
    onClick: Optional[str] = None
    onChange: Optional[str] = None
    onSubmit: Optional[str] = None
    onHover: Optional[str] = None
    onKeyPress: Optional[Dict[str, str]] = None  # {"Enter": "submitSearch", "Escape": "clearSearch"}
    
    # Static props (passed directly to Ant Design component)
    props: Dict[str, Any] = Field(default_factory=dict)
    
    # Dynamic props (computed at runtime from expressions)
    dynamic_props: Dict[str, str] = Field(default_factory=dict)
    # Examples:
    #   {"disabled": "state.isSubmitting", "loading": "state.isFetching"}
    #   {"options": "derived.vendorOptions.map(v => ({label: v, value: v}))"}
    #   {"badge_count": "derived.pendingCount"}
    
    # Styles
    styles: Dict[str, Any] = Field(default_factory=dict)
    
    # Dynamic styles (computed at runtime)
    dynamic_styles: Dict[str, str] = Field(default_factory=dict)
    # Examples:
    #   {"backgroundColor": "record.status === 'Active' ? '#f6ffed' : '#fff7e6'"}
    #   {"color": "record.priority === 'High' ? '#f5222d' : '#333'"}
    #   {"opacity": "state.isDisabled ? 0.5 : 1"}
    
    # CSS class (static + dynamic)
    class_name: Optional[str] = None
    dynamic_class: Optional[str] = None          # "record.status === 'Active' ? 'row-active' : 'row-inactive'"
    
    # Transitions/animations
    transitions: List[TransitionDef] = Field(default_factory=list)
    
    # Conditional rendering
    visible_when: Optional[str] = None           # "state.showAdvanced === true"
    disabled_when: Optional[str] = None          # "state.isSubmitting"
    
    # List rendering
    repeat: Optional[RepeatDef] = None
    
    # Slots (for component composition)
    slots: Dict[str, str] = Field(default_factory=dict)          # {"header": "headerComponent", "footer": "footerComponent"}
    
    # Accessibility
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
# 7. LAYOUT IR — Tree structure, layout types, zones, responsive
# ============================================================================

class LayoutDef(StrictBase):
    type: Literal["vertical", "horizontal", "grid", "sidebar", "stack"] = "vertical"
    gap: Optional[int] = None
    padding: Optional[str] = None
    columns: Optional[int] = None                # for grid
    column_template: Optional[str] = None        # "1fr 3fr", "280px 1fr"
    row_template: Optional[str] = None
    align_items: Optional[str] = None            # "center", "stretch"
    justify_content: Optional[str] = None        # "space-between", "center"
    wrap: bool = False
    min_height: Optional[str] = None
    overflow: Optional[str] = None               # "auto", "hidden", "scroll"

class LayoutZoneDef(StrictBase):
    zone_id: str
    component: str                               # root component_id for this zone
    anchor: str = "center"
    size_hint: str = "auto"                      # "full-width", "auto", "50%"
    z_layer: Literal["base", "overlay", "modal", "toast"] = "base"
    notes: str = ""

class ResponsiveOverride(StrictBase):
    """Override layout at a specific breakpoint."""
    breakpoint: str                              # "sm", "md", "lg"
    layout_overrides: Dict[str, LayoutDef] = Field(default_factory=dict)
    hidden_components: List[str] = Field(default_factory=list)
    visibility_overrides: Dict[str, str] = Field(default_factory=dict)  # component_id → "hidden" | "visible"

class LayoutIR(StrictBase):
    root: str                                    # root component_id
    children: Dict[str, List[str]] = Field(default_factory=dict)  # parent → [child1, child2, ...]
    layout: Dict[str, LayoutDef] = Field(default_factory=dict)    # component_id → layout config
    layout_zones: List[LayoutZoneDef] = Field(default_factory=list)
    responsive_overrides: List[ResponsiveOverride] = Field(default_factory=list)


# ============================================================================
# 8. NAVIGATION IR — Tabs, Modals, Drawers, Routes, Breadcrumbs
# ============================================================================

class TabDef(StrictBase):
    tab_id: str
    label: str
    icon: Optional[str] = None
    content_root: str                            # component_id that is root of this tab
    badge_expr: Optional[str] = None             # "derived.pendingCount"
    disabled_when: Optional[str] = None          # "state.isLocked"
    default: bool = False

class ModalDef(StrictBase):
    modal_id: str
    title: str
    title_expr: Optional[str] = None             # "dynamic: `Edit ${state.selectedItem.name}`"
    width: Optional[int] = None
    trigger_state: str                           # "state.showAddModal"
    content_root: str                            # component_id
    on_close_event: Optional[str] = None         # "onCloseAddModal"
    closable: bool = True
    mask_closable: bool = True
    footer_actions: List[str] = Field(default_factory=list)  # action_ids for footer buttons

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
    path: str                                    # "/orders", "/orders/:id"
    page_id: str                                 # which page IR to render
    label: str = ""
    icon: Optional[str] = None
    guard: Optional[str] = None                  # "state.user.isAuthenticated"
    params: List[str] = Field(default_factory=list)

class BreadcrumbDef(StrictBase):
    items: List[Dict[str, str]] = Field(default_factory=list)
    # [{"label": "Home", "path": "/"}, {"label": "Orders", "path": "/orders"}, {"label": "PO-001"}]

class NavigationIR(StrictBase):
    tabs: List[TabDef] = Field(default_factory=list)
    modals: Dict[str, ModalDef] = Field(default_factory=dict)
    drawers: Dict[str, DrawerDef] = Field(default_factory=dict)
    routes: List[RouteDef] = Field(default_factory=list)
    breadcrumb: Optional[BreadcrumbDef] = None
    default_tab: Optional[str] = None


# ============================================================================
# 9. REALTIME IR — Timers, Polling
# ============================================================================

class TimerDef(StrictBase):
    timer_id: str
    type: Literal["interval", "timeout", "countdown"] = "interval"
    interval_ms: int = 1000
    action: str                                  # event/action name to trigger on each tick
    auto_start: bool = True
    stop_when: Optional[str] = None              # "state.timerComplete === true"
    description: str = ""

class PollingDef(StrictBase):
    polling_id: str
    endpoint_id: str                             # references data_fetch_ir endpoint
    interval_ms: int = 30000
    active_when: Optional[str] = None            # "state.isLiveView === true"
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
# THE FINAL BUNDLE
# ============================================================================

class IRBundle(StrictBase):
    """
    Dalfin IR Bundle v3.5 — Complete template for ALL UI scenarios.
    
    AI reads this template and generates a valid IR JSON matching this structure.
    Code generator reads the IR and produces React + Ant Design code.
    
    Sections:
      page_ir         — page metadata, style, accessibility, responsive
      data_ir         — state, derived, custom types
      data_fetch_ir   — runtime API calls, loading/error states
      data_model_ir   — entities, relationships
      behaviour_ir    — events, actions, validation, side effects, chaining
      component_ir    — Ant Design components with dynamic props/styles/conditional/repeat
      layout_ir       — tree structure, layout types, zones, responsive overrides
      navigation_ir   — tabs, modals, drawers, routes, breadcrumbs
      realtime_ir     — timers, polling
      metadata        — version, generation info
    """
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
