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
    },
    "external_source_ref": {
      "source_id": "student_external",
      "snapshot_path": "db/external_db_snapshot.json",
      "db_path": "/db/student_data.db"
    },
    "sql_query_ir": {
      "sql_template": "SELECT table.col1, table.col2 FROM table WHERE (:search = '' OR table.col1 LIKE '%' || :search || '%') ORDER BY table.col1 LIMIT :limit OFFSET :offset",
      "params": [":limit", ":offset", ":search"],
      "default_page_size": 50,
      "max_page_size": 200
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


def _db_schema_context_block(schema_context: str | None) -> str:
    if schema_context and schema_context.strip():
        return f"""
External DB schema context (SQLite snapshot metadata):
{schema_context}
""".strip()
    return "External DB schema context is unavailable for this request."


def build_base_prompt(user_request: str, schema_context: str | None = None) -> str:
    db_block = _db_schema_context_block(schema_context)
    return f"""
Generate one JSON object for an IRBundle from this request:
{user_request}

{db_block}

Output requirements:
- Return JSON only. No markdown and no extra text.
- Use EXACTLY these root keys:
  page_ir, data_ir, data_model_ir, behaviour_ir, component_ir, layout_ir
- Do not add extra top-level keys.
- component_ir.library must be "antd".
- behaviour_ir.events/actions/feedback must be object maps (not lists).
- Event type must be exactly "mutation".
- Always design for a fullscreen responsive app:
  - page_ir.constraints must include "fullscreen_layout".
  - Root layout should fill the viewport (avoid fixed widths; prefer fluid/responsive layout).
  - Provide sensible responsive behavior for small screens (stack/collapse/hide where appropriate).
- Every id referenced must exist:
  - layout_ir.root must exist in component_ir.components
  - layout_ir.children keys and values must exist in component_ir.components
  - layout_ir.layout keys must exist in component_ir.components
  - layout_ir.layout_zones[].component must exist in component_ir.components
  - behaviour_ir.actions[*].target_component_id must exist in component_ir.components
  - component_ir.components[*].onClick must reference an existing actionId or eventId (or be null)
- If a field is not needed, omit it only if the schema allows omitting it; otherwise keep it with a valid empty/default.
- Keep all objects compliant with extra="forbid" (no unknown keys).
- If the user requests data that should come from the external DB:
  - Populate `data_model_ir.external_source_ref` and `data_model_ir.sql_query_ir`.
  - `sql_query_ir.sql_template` must be one SELECT query (or WITH...SELECT), never INSERT/UPDATE/DELETE/DDL.
  - SQL must use only tables/columns from the provided external DB schema context.
  - SQL must include pagination placeholders: `LIMIT :limit OFFSET :offset`.
  - Allowed params are `:limit`, `:offset`, and optional `:search`.
  - Set `default_page_size` to 50 and `max_page_size` to 200 unless user explicitly asks otherwise.
  - Add data runtime state keys under `data_ir.state` if missing:
    - `rows` (array, initial []), `loading` (boolean, initial false), `error` (string, initial ""),
      `page` (number, initial 1), `pageSize` (number, initial 50), `total` (number, initial 0).
- If external DB data is not needed, omit `external_source_ref` and `sql_query_ir`.

Use this exact structural template and replace placeholders with meaningful IDs/values:
{IR_BUNDLE_TEMPLATE}
""".strip()


def build_retry_prompt(
    user_request: str,
    validation_error: Exception,
    raw_text: str,
    schema_context: str | None = None,
) -> str:
    db_block = _db_schema_context_block(schema_context)
    return f"""
Your previous output is INVALID for IRBundle.
Validation errors:
{validation_error}

{db_block}

Rewrite the previous JSON so it becomes valid.
Return one corrected JSON object only with these exact root keys:
page_ir, data_ir, data_model_ir, behaviour_ir, component_ir, layout_ir.

Critical typing rules:
- data_model_ir.entities[*].fields/computed/display_fields must be lists of strings only.
- behaviour_ir.actions[*].validation_rules must be a list of strings only.
- component_ir.library must be exactly "antd".
- If you include data_model_ir.sql_query_ir:
  - sql_template must remain single-statement SELECT/CTE SELECT.
  - Use only allowlisted tables/columns from schema context.
  - Include LIMIT :limit OFFSET :offset placeholders.
  - params must include :limit and :offset.

Required structure template:
{IR_BUNDLE_TEMPLATE}

Original request:
{user_request}

Previous invalid output:
{raw_text}
""".strip()


def build_sql_retry_prompt(
    user_request: str,
    sql_error: Exception,
    raw_text: str,
    schema_context: str | None = None,
) -> str:
    db_block = _db_schema_context_block(schema_context)
    return f"""
Your previous output produced an INVALID SQL query in data_model_ir.sql_query_ir.
SQL validation error:
{sql_error}

{db_block}

Rewrite the IR JSON so it is valid and SQL-safe.
Return JSON only with exact root keys:
page_ir, data_ir, data_model_ir, behaviour_ir, component_ir, layout_ir.

SQL requirements:
- Exactly one SELECT statement (or WITH ... SELECT).
- Use only tables/columns listed in schema context.
- Include pagination placeholders exactly: LIMIT :limit OFFSET :offset.
- Never use forbidden SQL operations (INSERT/UPDATE/DELETE/DDL/PRAGMA/ATTACH).
- params must include :limit and :offset.
- default_page_size should be <= max_page_size and max_page_size <= 200.

Required structure template:
{IR_BUNDLE_TEMPLATE}

Original request:
{user_request}

Previous invalid output:
{raw_text}
""".strip()
