def build_react_prompt(ir_json: str) -> str:
    return f"""
You are a senior React engineer.
Convert the provided IRBundle JSON into a complete React component file in TypeScript.

Requirements:
- Output only TSX code, no markdown.
- Use Ant Design components for UI.
- Export default function `GeneratedApp()`.
- Code must compile cleanly with strict TypeScript (`tsc -b`) in a Vite React app.
- Avoid unused imports and unused variables.
- Do not use `App.message`. For notifications, use `message.useMessage()` and render `contextHolder`.
- Do not use a default `React` import.
- Do not annotate the component return type with `JSX.Element`.
- If style typing is needed, use `import type` from React (for example, `CSSProperties`).
- Under `verbatimModuleSyntax`, import type-only symbols with `import type` (including third-party library types).
- Handle nullable numeric state safely: copy to local `const` variables, guard for null/invalid values, and only perform arithmetic after narrowing.
- Build React state from `data_ir.state`.
- Build derived values from `data_ir.derived` (prefer `useMemo` where helpful).
- Implement event handlers from `behaviour_ir.events`.
- Respect component labels, bind, and onClick links from `component_ir.components`.
- Respect vertical/horizontal/grid hints from `layout_ir.layout`.
- Apply `component_ir.theme.primaryColor` and per-component styles where possible.
- If `data_model_ir.sql_query_ir` exists:
  - Use SQLite WASM in the browser via `sql.js`.
  - Load DB from `data_model_ir.external_source_ref.db_path` (fallback `/db/student_data.db`).
  - Configure `initSqlJs({{ locateFile: () => '/db/sql-wasm.wasm' }})`.
  - Use SQL from `data_model_ir.sql_query_ir.sql_template` and bind params safely.
  - Coerce pagination values with `Number(...)` and convert to positive integers before SQL execution.
  - NEVER pass non-integer/NaN values to SQLite `LIMIT` or `OFFSET`.
  - To avoid SQLite datatype mismatch, construct page SQL with sanitized integer literals for `LIMIT/OFFSET`.
  - Do not use named/positional SQLite bindings for `LIMIT/OFFSET`.
  - Implement server-style pagination with page/pageSize state and `LIMIT :limit OFFSET :offset`.
  - Query total count separately for pagination (`SELECT COUNT(*) ...`) if needed.
  - Populate `rows`, `loading`, `error`, `page`, `pageSize`, and `total` runtime state.
  - Do not leave any declared state unused; render `error` visibly when present.
  - Avoid implicit `any` in callbacks (for example table change handlers and row mapping callbacks).
  - Avoid unsafe object casts from SQL result rows; map row indexes explicitly into typed objects.
  - Render an AntD `Table` with pagination hooked to page queries.
- Keep code readable and runnable.
- Do not add explanations.

IRBundle JSON:
{ir_json}
""".strip()
