# UIAgent

## Professional Project Structure

```text
Tools/
  ir_generation.py              # CLI entrypoint: NL request -> IR JSON
  ir_to_react.py                # CLI entrypoint: IR JSON -> TSX
  db_snapshot.py                # CLI entrypoint: SQLite -> external snapshot JSON
  ir_structure.py               # Backward-compatible schema export
  generated_ir.json             # Generated IR output
  generated_app.tsx             # Generated React output
  ir_pipeline/
    llm/
      client.py                 # AWS Bedrock Anthropic/LangChain model setup
    prompts/
      ir_generation.py          # IR generation prompt builders
      react_generation.py       # React generation prompt builder
    schemas/
      ir_bundle.py              # Pydantic IRBundle schema
    services/
      ir_generation_service.py  # IR generation orchestration
      react_generation_service.py # React generation orchestration
    utils/
      extractors.py             # JSON/code block extraction helpers
      normalization.py          # LLM output normalization helpers
      db_snapshot.py            # snapshot generation + schema context helpers
      sql_safety.py             # SELECT-only SQL validation/normalization
```

## Run

From `Tools`:

```powershell
uv run ir_generation.py
uv run ir_to_react.py
uv run db_snapshot.py
```

From repo root, the same commands are:

```powershell
uv run Tools/ir_generation.py
uv run Tools/ir_to_react.py
uv run Tools/db_snapshot.py
```

`ir_generation.py` writes IR to `Tools/generated_ir.json` (overwrite enabled by default).
When `db/student_data.db` exists, IR generation now auto-refreshes `db/external_db_snapshot.json`,
validates any `data_model_ir.sql_query_ir.sql_template` with SELECT-only safety guards, and syncs DB
to `ui-compiler-poc/frontend/public/db/student_data.db` for frontend runtime reads.
If `ui-compiler-poc/frontend/node_modules/sql.js/dist/sql-wasm.wasm` exists, it is also copied to
`ui-compiler-poc/frontend/public/db/sql-wasm.wasm`.

Bedrock/Claude config is read from `.env` (or environment variables):

```dotenv
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
AWS_SESSION_TOKEN=...  # optional
AWS_REGION=us-east-1
BEDROCK_MODEL_ID=global.anthropic.claude-sonnet-4-5-20250929-v1:0
```

For Sonnet 4.5 on Bedrock, use an inference profile ID/ARN when required (for example `global.anthropic.claude-sonnet-4-5-20250929-v1:0`).

`ir_to_react.py` now writes generated React code directly to:

- `ui-compiler-poc/frontend/src/App.tsx`

so the frontend can be run immediately without manual copying.

## Chat Mode (Easiest)

This is the best way to use the system like a normal end user.

From repo root:

```powershell
uv run Tools/chat.py
```

From `Tools`:

```powershell
uv run chat.py
```

Useful flags:

```powershell
uv run chat.py --no-compile
uv run chat.py --model global.anthropic.claude-sonnet-4-5-20250929-v1:0
```

## Manual Test (Non-Technical User Flow)

1. Start chat:

```powershell
uv run Tools/chat.py
```

2. At the first prompt, type:

```text
I need a simple page where I can add students and see them in a table.
```

3. After generation, try edits in plain English:

```text
Make it look cleaner with softer colors.
Please rename the add button to Save Student.
I only care about name and marks in the table.
history
save ir my_session.ir.json
exit
```

4. Verify outputs:
- IR updated at `Tools/generated_ir.json`
- Optional saved snapshot at `Tools/my_session.ir.json`
- React output updated at `ui-compiler-poc/frontend/src/App.tsx` (if compile is enabled)

## PatchOps Test

PatchOps applies patch files to an existing IR.

From repo root:

```powershell
uv run Tools/patch_ops.py --patch example.patch.json
```

From `Tools`:

```powershell
uv run patch_ops.py --patch example.patch.json
```

Notes:
- `example.patch.json` assumes a student-dashboard style IR with matching component IDs.
- If your current `generated_ir.json` does not match those IDs, either regenerate IR first via `chat.py` or use a patch file that matches your current IR.
- For inspection without writing files, add `--dry-run`.

## Optional Unit Tests

`pytest` is not in default dependencies, so install it once:

```powershell
uv pip install pytest
```

Then run:

```powershell
uv run python -m pytest Tools/tests/test_patchops.py -v
```

## Logs

- Log file is maintained automatically at:
  - `Tools/logs/uia.log`
- The file is rotated automatically (max ~1MB per file, 5 backups).
