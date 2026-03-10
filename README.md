# UIAgent Deployment Guide

UIAgent exposes a FastAPI endpoint that takes a prompt and runs the full generation flow:

1. Prompt -> IR JSON
2. IR JSON -> React TSX
3. Optional sync to `ui-compiler-poc/frontend/src/App.tsx`

Current API endpoint:

- `POST /v1/generate`

## Repository Layout

```text
UIAgent/
  ui_generation/
    api/main.py                      # FastAPI app
    cli/                             # CLI tools
    ir_pipeline/                     # Core generation services
    generated/ir/                    # Generated IR output
    generated/react/                 # Generated React output
    logs/                            # App logs + script transcripts
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

1. Create your env file:

```powershell
copy .env.example .env
```

2. Fill required values in `.env`:

- `AWS_PROFILE` or `AWS_ACCESS_KEY_ID` + `AWS_SECRET_ACCESS_KEY`
- `BEDROCK_AWS_REGION` (or `AWS_REGION`)
- `BEDROCK_MODEL_ID`

## Install Dependencies

```powershell
uv sync
```

## Run API (Local Validation)

```powershell
uv run uvicorn ui_generation.api.main:app --host 127.0.0.1 --port 8000 --reload
```

Open:

- `http://127.0.0.1:8000/docs`
- `http://127.0.0.1:8000/openapi.json`

## API Contract

Endpoint:

- `POST /v1/generate`

Request body:

```json
{
  "prompt": "Build a dashboard with summary cards and filters",
  "images_dir": "ui_generation/uploads",
  "model": "global.anthropic.claude-sonnet-4-5-20250929-v1:0",
  "overwrite": true,
  "sync_frontend_app": true
}
```

Response:

- `status`
- `ir` (generated IR object)
- `react_code` (generated TSX source)

Common status codes:

- `200` success
- `400` invalid input
- `409` output file exists and overwrite disabled
- `422` IR generation/validation failed
- `500` internal error

## Smoke Test

```powershell
curl -X POST "http://127.0.0.1:8000/v1/generate" `
  -H "Content-Type: application/json" `
  -d "{\"prompt\":\"Create a simple analytics dashboard\",\"overwrite\":true,\"sync_frontend_app\":true}"
```

## Production Start Command

Run without `--reload`:

```bash
uv run uvicorn ui_generation.api.main:app --host 0.0.0.0 --port 8000 --workers 1
```

Use `--workers 1` by default because generation is heavy and writes shared output files.

## Systemd Example (Linux)

Create `/etc/systemd/system/uiagent.service`:

```ini
[Unit]
Description=UIAgent FastAPI Service
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/opt/uiagent
EnvironmentFile=/opt/uiagent/.env
ExecStart=/usr/local/bin/uv run uvicorn ui_generation.api.main:app --host 0.0.0.0 --port 8000 --workers 1
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl daemon-reload
sudo systemctl enable uiagent
sudo systemctl start uiagent
sudo systemctl status uiagent
```

## Reverse Proxy Notes

Place Nginx/ALB in front of the service for TLS and routing.

Recommended:

1. Keep API on private port `8000`
2. Configure upstream timeout to allow LLM latency
3. Restrict ingress to trusted callers (VPN, private subnet, or gateway auth)

## Logs and Artifacts

- App logs: `ui_generation/logs/uia.log`
- Generated IR: `ui_generation/generated/ir/generated_ir.json`
- Generated React: `ui_generation/generated/react/generated_app.tsx`

## Operational Notes

1. `sync_frontend_app=true` overwrites `ui-compiler-poc/frontend/src/App.tsx`.
2. Calls can take several seconds due to model invocation latency.
3. Keep `.env` out of source control.

