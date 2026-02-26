# UIAgent

## Professional Project Structure

```text
Tools/
  ir_generation.py              # CLI entrypoint: NL request -> IR JSON
  ir_to_react.py                # CLI entrypoint: IR JSON -> TSX
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
```

## Run

From `Tools`:

```powershell
uv run ir_generation.py
uv run ir_to_react.py
```

`ir_generation.py` writes IR to `Tools/generated_ir.json` (overwrite enabled by default).

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

## Logs

- Log file is maintained automatically at:
  - `Tools/logs/uia.log`
- The file is rotated automatically (max ~1MB per file, 5 backups).
