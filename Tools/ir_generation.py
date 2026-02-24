import json
import os
from json import JSONDecodeError
from typing import Any

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from pydantic import ValidationError

from ir_structure import IRBundle


def _extract_json_object(text: str) -> str:
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or start >= end:
        raise JSONDecodeError("No JSON object found in model response.", text, 0)
    return text[start : end + 1]


def _normalize_string_list(values: Any) -> Any:
    if not isinstance(values, list):
        return values

    normalized: list[str] = []
    for item in values:
        if isinstance(item, str):
            normalized.append(item)
            continue

        if isinstance(item, dict):
            extracted = None
            for key in ("key", "name", "field", "id"):
                candidate = item.get(key)
                if isinstance(candidate, str):
                    extracted = candidate
                    break
            normalized.append(extracted or json.dumps(item, sort_keys=True))
            continue

        normalized.append(str(item))

    return normalized


def _normalize_validation_rule(rule: Any) -> str:
    if isinstance(rule, str):
        return rule
    if isinstance(rule, dict):
        name = rule.get("rule")
        target = rule.get("target")
        if isinstance(name, str) and isinstance(target, str):
            extras = []
            for key, value in rule.items():
                if key in {"rule", "target"}:
                    continue
                extras.append(f"{key}={value}")
            return f"{name}:{target}" if not extras else f"{name}:{target}:{':'.join(extras)}"
        return json.dumps(rule, sort_keys=True)
    return str(rule)


def _normalize_common_mismatches(payload: dict[str, Any]) -> dict[str, Any]:
    data_model = payload.get("data_model_ir")
    if isinstance(data_model, dict):
        entities = data_model.get("entities")
        if isinstance(entities, dict):
            for entity in entities.values():
                if not isinstance(entity, dict):
                    continue
                for key in ("fields", "computed", "display_fields"):
                    if key in entity:
                        entity[key] = _normalize_string_list(entity[key])

    behaviour = payload.get("behaviour_ir")
    if isinstance(behaviour, dict):
        actions = behaviour.get("actions")
        if isinstance(actions, dict):
            for action in actions.values():
                if not isinstance(action, dict):
                    continue
                rules = action.get("validation_rules")
                if isinstance(rules, list):
                    action["validation_rules"] = [_normalize_validation_rule(rule) for rule in rules]

    component = payload.get("component_ir")
    if isinstance(component, dict):
        component["library"] = "antd"

    return payload


def _delete_path(root: Any, loc: tuple[Any, ...]) -> bool:
    if not loc:
        return False

    current = root
    for key in loc[:-1]:
        if isinstance(current, dict) and key in current:
            current = current[key]
            continue
        if isinstance(current, list) and isinstance(key, int) and 0 <= key < len(current):
            current = current[key]
            continue
        return False

    last = loc[-1]
    if isinstance(current, dict) and last in current:
        del current[last]
        return True
    if isinstance(current, list) and isinstance(last, int) and 0 <= last < len(current):
        current.pop(last)
        return True
    return False


def _drop_extra_forbidden_fields(payload: dict[str, Any], exc: ValidationError) -> bool:
    changed = False
    for error in exc.errors():
        if error.get("type") != "extra_forbidden":
            continue
        loc = error.get("loc")
        if isinstance(loc, tuple):
            changed = _delete_path(payload, loc) or changed
    return changed


load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

model = ChatOpenAI(
    model="gpt-5.2",
    temperature=0,
    api_key=api_key,
)

user_request = input("Enter your UI request: ").strip()

template = """
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
          { "target": "state.stateKey", "expr": "1 + 2" }
        ]
      }
    },
    "actions": {
      "actionId": {
        "action_id": "actionId",
        "trigger": "button_click",
        "target_component_id": "componentId",
        "operation": "string",
        "payload": {},
        "validation_rules": [],
        "requires_confirmation": false,
        "updates": [
          { "target": "state.stateKey", "expr": "state.stateKey + 1" }
        ]
      }
    },
    "feedback": {
      "actionId": {
        "action_id": "actionId",
        "loading_indicator": "spinner|null",
        "success_message": "string|null",
        "error_message": "string|null",
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


base_prompt = f"""
Generate one JSON object for an IRBundle from this request:
{user_request}

Output requirements:
- Return JSON only. No markdown and no extra text.
- Use EXACTLY these root keys:
  page_ir, data_ir, data_model_ir, behaviour_ir, component_ir, layout_ir
- Do not add extra top-level keys.
- component_ir.library must be "antd".
- behaviour_ir.events/actions/feedback must be object maps (not lists).
- Event type must be exactly "mutation".
- Every id referenced must exist:
  - layout_ir.root must exist in component_ir.components
  - layout_ir.children keys and values must exist in component_ir.components
  - layout_ir.layout keys must exist in component_ir.components
  - layout_ir.layout_zones[].component must exist in component_ir.components
  - behaviour_ir.actions[*].target_component_id must exist in component_ir.components
  - component_ir.components[*].onClick must reference an existing actionId or eventId (or be null)
- If a field is not needed, omit it only if the schema allows omitting it; otherwise keep it with a valid empty/default.
- Keep all objects compliant with extra="forbid" (no unknown keys).

Use this exact structural template and replace placeholders with meaningful IDs/values:
{template}
""".strip()

prompt = base_prompt
last_error = None
last_raw_text = ""
success = False

for attempt in range(1, 4):
    response = model.invoke(prompt)
    raw_text = response.content if isinstance(response.content, str) else str(response.content)
    last_raw_text = raw_text
    try:
        parsed = json.loads(_extract_json_object(raw_text))
        normalized = _normalize_common_mismatches(parsed)
        try:
            irbundle = IRBundle.model_validate(normalized)
        except ValidationError as exc:
            if not _drop_extra_forbidden_fields(normalized, exc):
                raise
            irbundle = IRBundle.model_validate(normalized)
        print(irbundle.model_dump_json(indent=2))
        success = True
        last_error = None
        break
    except (JSONDecodeError, ValidationError) as exc:
        last_error = exc
        if attempt == 3:
            raise
        prompt = f"""
Your previous output is INVALID for IRBundle.
Validation errors:
{exc}

Rewrite the previous JSON so it becomes valid.
Return one corrected JSON object only with these exact root keys:
page_ir, data_ir, data_model_ir, behaviour_ir, component_ir, layout_ir.

Critical typing rules:
- data_model_ir.entities[*].fields/computed/display_fields must be lists of strings only.
- behaviour_ir.actions[*].validation_rules must be a list of strings only.
- component_ir.library must be exactly "antd".

Required structure template:
{template}

Original request:
{user_request}

Previous invalid output:
{raw_text}
"""

if not success and last_error is not None:
    raise RuntimeError(
        "Failed to generate a valid IRBundle after 3 attempts.\n"
        f"Last validation error: {last_error}\n"
        f"Last model output:\n{last_raw_text}"
    )
