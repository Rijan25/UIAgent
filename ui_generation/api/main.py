from __future__ import annotations

import shutil
import sys
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

ROOT_DIR = Path(__file__).resolve().parents[2]
UI_GENERATION_DIR = ROOT_DIR / "ui_generation"
DEFAULT_IR_OUTPUT = UI_GENERATION_DIR / "generated" / "ir" / "generated_ir.json"
DEFAULT_REACT_OUTPUT = UI_GENERATION_DIR / "generated" / "react" / "generated_app.tsx"
DEFAULT_FRONTEND_APP = ROOT_DIR / "ui-compiler-poc" / "frontend" / "src" / "App.tsx"

if str(UI_GENERATION_DIR) not in sys.path:
    sys.path.insert(0, str(UI_GENERATION_DIR))

from ir_pipeline.llm import DEFAULT_CLAUDE_MODEL
from ir_pipeline.services import generate_ir_bundle, generate_react_code, write_ir_bundle
from ir_pipeline.utils import configure_logging, get_logger, log_timed_step


class GenerateRequest(BaseModel):
    prompt: str = Field(min_length=1, description="Natural language prompt for UI generation.")
    model: str = Field(default=DEFAULT_CLAUDE_MODEL, description="Bedrock model ID.")
    overwrite: bool = Field(default=True, description="Overwrite existing generated files if present.")
    sync_frontend_app: bool = Field(
        default=True,
        description="Copy generated TSX to ui-compiler-poc/frontend/src/App.tsx.",
    )


class GenerateResponse(BaseModel):
    status: str
    ir: dict[str, Any]
    react_code: str


app = FastAPI(title="UIAgent API", version="1.0.0")
configure_logging()
logger = get_logger("api.main")


@app.post("/v1/generate", response_model=GenerateResponse)
def generate_ui(payload: GenerateRequest) -> GenerateResponse:
    prompt = payload.prompt.strip()
    if not prompt:
        raise HTTPException(status_code=400, detail="prompt cannot be empty")

    try:
        with log_timed_step(logger, "API request: generate pipeline", model=payload.model):
            with log_timed_step(logger, "API step: Generate IR", model=payload.model):
                bundle = generate_ir_bundle(user_request=prompt, model_name=payload.model)

            with log_timed_step(logger, "API step: Write IR"):
                write_ir_bundle(bundle=bundle, output_path=DEFAULT_IR_OUTPUT, overwrite=payload.overwrite)

            with log_timed_step(logger, "API step: Generate React", model=payload.model):
                react_code = generate_react_code(ir_bundle=bundle, model_name=payload.model)

            with log_timed_step(logger, "API step: Write React"):
                DEFAULT_REACT_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
                if DEFAULT_REACT_OUTPUT.exists() and not payload.overwrite:
                    raise FileExistsError(f"Output file already exists: {DEFAULT_REACT_OUTPUT}")
                DEFAULT_REACT_OUTPUT.write_text(react_code + "\n", encoding="utf-8")

            if payload.sync_frontend_app:
                with log_timed_step(logger, "API step: Sync frontend App.tsx"):
                    DEFAULT_FRONTEND_APP.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(DEFAULT_REACT_OUTPUT, DEFAULT_FRONTEND_APP)

        return GenerateResponse(
            status="ok",
            ir=bundle.model_dump(mode="json"),
            react_code=react_code,
        )
    except FileExistsError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("Unhandled API failure")
        raise HTTPException(status_code=500, detail=f"Internal server error: {exc}") from exc
