# UIAgent

UIAgent can generate a UI IR (JSON) from either:

1. A text prompt, or
2. A folder of UI reference images (2–3 screenshots is typical)

Then it converts IR -> React TSX and can optionally sync it into the preview frontend.

## Repository Layout

```text
UIAgent/
  ui_generation/
    api/main.py                      # FastAPI app
    cli/                             # CLI tools
    ir_pipeline/                     # Core generation services
    generated/ir/                    # Generated IR output
    generated/react/                 # Generated React output
    uploads/                         # Local image inputs (ignored by git)
    PATCHOPS.md                      # PatchOps docs
    patch_ops.py                     # PatchOps CLI
    chat.py                          # Interactive edit loop
  ui-compiler-poc/frontend/          # Frontend preview app
  .env.example
  pyproject.toml
```

## Prerequisites

1. Python 3.10+
2. `uv` installed
3. AWS Bedrock access for the configured model
4. Valid AWS credentials and region configuration

## Environment Setup

```powershell
copy .env.example .env
uv sync
```

Set in `.env` (or your shell):

- `AWS_PROFILE` or `AWS_ACCESS_KEY_ID` + `AWS_SECRET_ACCESS_KEY` (+ optional `AWS_SESSION_TOKEN`)
- `BEDROCK_AWS_REGION` (or `AWS_REGION`)
- `BEDROCK_MODEL_ID` (optional; defaults are provided in code)

## Run API (Local Validation)

```powershell
uv run uvicorn ui_generation.api.main:app --host 127.0.0.1 --port 8000 --reload
```

Open:

- `http://127.0.0.1:8000/docs`

### `POST /v1/generate`

Request body example:

```json
{
  "prompt": "Build a dashboard with summary cards and filters",
  "images_dir": "ui_generation/uploads",
  "model": "global.anthropic.claude-sonnet-4-5-20250929-v1:0",
  "overwrite": true,
  "sync_frontend_app": true
}
```

Notes:

- You can omit `prompt` when using `images_dir` (images-only generation).
- `images_limit` is optional (defaults to all images in the folder, capped for safety).

## Run Pipeline (CLI)

Generate IR from images (then optionally type edits, or press Enter):

```powershell
uv run python ui_generation/cli/ir_generation.py --images-dir ui_generation/uploads
```

Run full pipeline (IR -> React, no dev server):

```powershell
uv run python main.py --images-dir ui_generation/uploads --no-serve
```

## PatchOps (Optional)

Docs: `ui_generation/PATCHOPS.md`

```powershell
uv run python ui_generation/patch_ops.py --patch ui_generation/example.patch.json --dry-run
```

## Chat Mode (Optional)

```powershell
uv run python ui_generation/chat.py
```

## Logs and Artifacts

- Logs: `ui_generation/logs/`
- Generated IR: `ui_generation/generated/ir/generated_ir.json`
- Generated React: `ui_generation/generated/react/generated_app.tsx`

