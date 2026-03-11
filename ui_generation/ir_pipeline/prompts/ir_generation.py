IR_BUNDLE_TEMPLATE = """
{
  "page_ir": {
    "page_goal": "string",
    "style": {
      "tone": "string|null",
      "theme": "string|null",
      "density": "string|null",
      "color_intent": "string|null"
    },
    "accessibility": {
      "required_labels": []
    },
    "responsive": {
      "breakpoints": {},
      "collapse_rules": [],
      "hidden_on_small": []
    },
    "constraints": []
  },
  "data_ir": {
    "state": {
      "stateKey": {
        "type": "number|string|boolean|array|object|enum|date",
        "initial": null,
        "required": false,
        "constraints": {}
      }
    },
    "derived": {
      "derivedKey": {
        "type": "number|string|boolean|array|object|enum|date",
        "expr": "stateKey + 1"
      }
    }
  },
  "data_model_ir": {
    "entities": {
      "entityKey": {
        "name": "string",
        "fields": [],
        "computed": [],
        "display_fields": [],
        "filters": []
      }
    }
  },
  "behaviour_ir": {
    "events": {
      "eventId": {
        "type": "mutation",
        "updates": [
          { "target": "state.stateKey", "expr": "new_value" }
        ]
      }
    },
    "actions": {
      "actionId": {
        "action_id": "actionId",
        "trigger": "button_click",
        "target_component_id": "componentId",
        "operation": "custom",
        "payload": {},
        "validation_rules": [],
        "requires_confirmation": false,
        "updates": [
          { "target": "state.stateKey", "expr": "state.stateKey + 1" }
        ],
        "side_effects": [
          { "type": "toast", "config": { "message": "Done!", "type": "success" } }
        ]
      }
    },
    "feedback": {
      "actionId": {
        "action_id": "actionId",
        "loading_indicator": "spinner",
        "success_message": "Saved successfully",
        "error_message": "Something went wrong",
        "ui_updates": []
      }
    }
  },
  "component_ir": {
    "library": "antd",
    "theme": {
      "primaryColor": "#1677ff",
      "secondaryColor": "#000000",
      "fontFamily": "string",
      "borderRadius": 8
    },
    "components": {
      "componentId": {
        "type": "string",
        "label": "string|null",
        "bind": "string|null",
        "onClick": "string|null",
        "props": {},
        "styles": {}
      }
    }
  },
  "layout_ir": {
    "root": "root_container_id",
    "children": {
      "root_container_id": ["componentId"]
    },
    "layout": {
      "root_container_id": { "type": "vertical|horizontal|grid", "gap": 12 }
    },
    "layout_zones": [
      {
        "zone_id": "zoneId",
        "component": "componentId",
        "anchor": "center|bottom-right|top-left",
        "size_hint": "auto|full-width|40%",
        "z_layer": "base|overlay",
        "notes": "string|null"
      }
    ]
  }
}
""".strip()

_SYSTEM_PROMPT = """You are a senior UI architect. Your only task is to convert a UI description
into a valid IRBundle JSON document. You have deep expertise in Ant Design and React.

Output rules (non-negotiable):
1. Return ONLY valid JSON — no markdown, no prose, no explanations.
2. Use EXACTLY these root keys: page_ir, data_ir, data_model_ir,
   behaviour_ir, component_ir, layout_ir.
3. component_ir.library must be "antd".
4. behaviour_ir.events/actions/feedback are object maps, not arrays.
5. Event type is always "mutation".

BEHAVIOUR_IR SCHEMA RULES (critical):
- actions[*].operation MUST be one of: "create", "update", "delete", "read", "custom".
  NEVER invent values like "calculate_grades" — use "custom" for any non-CRUD operation.
- actions[*].action_id MUST be present and match the object's key.
  CORRECT:  "myAction": { "action_id": "myAction", "trigger": "button_click", ... }
  WRONG:    "myAction": { "operation": "custom", ... }   <- missing action_id and trigger
- actions[*].trigger is REQUIRED. Use: "button_click", "form_submit", "input_change", "row_click".
- actions[*].side_effects is a list of SideEffectDef objects, NOT strings.
  CORRECT:  "side_effects": [{"type": "toast", "config": {"message": "Done!", "type": "success"}}]
  WRONG:    "side_effects": ["update_student1_percentage"]   <- strings are not allowed here
  Allowed side_effect types: "toast", "navigate", "refresh", "modal_open", "modal_close",
  "drawer_open", "drawer_close", "download", "clipboard", "reset_state", "api_call", "custom".
- feedback[*].action_id is REQUIRED and must match the feedback entry's key.
  CORRECT:  "myFeedback": { "action_id": "myFeedback", "success_message": "Done" }
  WRONG:    "myFeedback": {}   <- action_id is missing

LAYOUT_IR ROOT FIELD (critical):
- layout_ir.root MUST be a plain string containing a component ID.
  CORRECT:   "root": "main_container"
  WRONG:     "root": {"id": "main_container", "type": "vertical"}   <- never do this
- layout_ir.layout values are where layout type/gap/etc go, NOT inside root.

REFERENTIAL INTEGRITY (critical — validate before returning):
- layout_ir.root value MUST exist as a key in component_ir.components.
- Every key in layout_ir.children MUST exist in component_ir.components.
- Every value inside layout_ir.children arrays MUST exist in component_ir.components.
- Every key in layout_ir.layout MUST exist in component_ir.components.
- layout_ir.layout_zones[].component MUST exist in component_ir.components.
- behaviour_ir.actions[*].target_component_id MUST exist in component_ir.components.
- component_ir.components[*].onClick MUST reference an existing actionId or eventId, or be null.

LAYOUT DEFAULTS:
- Root container: flex column, min-height: 100vh, width: 100%.
- Prefer fluid widths. Avoid fixed pixel widths on containers.
- Stack vertically on small screens."""


def build_base_prompt(user_request: str) -> str:
    return f"""{_SYSTEM_PROMPT}

Generate an IRBundle for this request:
{user_request}

Use this structure as your guide — replace ALL placeholder keys/values with meaningful ones:
{IR_BUNDLE_TEMPLATE}

Double-check referential integrity before returning. Return JSON only.""".strip()


def build_retry_prompt(
    user_request: str,
    validation_error: Exception,
    raw_text: str,
    max_raw_chars: int = 6000,
) -> str:
    truncated = raw_text[:max_raw_chars] + ("…[truncated]" if len(raw_text) > max_raw_chars else "")
    error_summary = str(validation_error)[:1500]

    return f"""{_SYSTEM_PROMPT}

The IRBundle JSON you returned failed validation.

=== VALIDATION ERRORS ===
{error_summary}

=== CRITICAL REMINDER ===
- layout_ir.root must be a plain string (a component ID), NOT an object.
  CORRECT:  "root": "main_container"
  WRONG:    "root": {{"id": "main_container", ...}}
- actions[*].operation must be one of: "create", "update", "delete", "read", "custom". Never invent values.
- actions[*].action_id and actions[*].trigger are REQUIRED fields on every action.
- actions[*].side_effects must be a list of objects with "type" and "config" keys, NOT a list of strings.
  CORRECT:  [{{"type": "toast", "config": {{"message": "Done!"}}}}]
  WRONG:    ["update_student1_percentage"]
- feedback[*].action_id is REQUIRED on every feedback entry and must match its key.
- data_model_ir.entities[*].fields/computed/display_fields must be lists of strings only.
- behaviour_ir.actions[*].validation_rules must be a list of strings only.
- component_ir.library must be exactly "antd".

=== INSTRUCTIONS ===
Fix ONLY the fields mentioned in the errors above.
Return the corrected complete JSON (all root keys required).
Return JSON only — no markdown, no preamble.

Original request: {user_request}

=== YOUR PREVIOUS OUTPUT (fix this) ===
{truncated}""".strip()