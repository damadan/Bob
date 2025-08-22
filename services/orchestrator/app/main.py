from pathlib import Path
from typing import Dict, List, Any
import os

from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from .config import settings


app = FastAPI(title="MCP Orchestrator", version="0.0.1")

# Enable permissive CORS so the simple HTML client can access the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Resolve the path to the static directory relative to this file
STATIC_DIR = Path(__file__).resolve().parent.parent / "static"

# Serve static assets (like the index.html) from /static
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


class RunRequest(BaseModel):
    project_id: str
    priced_bom: Dict[str, Any] = {}
    filenames: Dict[str, str] = {}


class ChatRequest(BaseModel):
    message: str


@app.get("/")
async def index() -> FileResponse:  # pragma: no cover - simple static file
    """Serve the minimal HTML client."""
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/health")
async def health() -> Dict[str, str]:
    return {"status": "ok"}


def _build_artifacts(project_id: str, filenames: Dict[str, str]) -> Dict[str, str]:
    base = str(settings.MCP_BASE_URL).rstrip("/")
    artifacts: Dict[str, str] = {}
    for kind, name in filenames.items():
        artifacts[f"{kind}_url"] = f"{base}/mcp/material/download/{project_id}/outputs/{name}"
    return artifacts


@app.post("/run")
async def run(req: RunRequest) -> Dict[str, Any]:
    artifacts = _build_artifacts(req.project_id, req.filenames)
    return {"priced_bom": req.priced_bom, "artifacts": artifacts}


@app.post("/run_multipart")
async def run_multipart(project_id: str, file: UploadFile = File(...)) -> Dict[str, Any]:
    _ = await file.read()
    base_name, _ = os.path.splitext(file.filename)
    filenames = {
        "excel": f"{base_name}.xlsx",
        "json": f"{base_name}.json",
        "pdf": f"{base_name}.pdf",
    }
    artifacts = _build_artifacts(project_id, filenames)
    return {"priced_bom": {}, "artifacts": artifacts}


@app.post("/chat")
async def chat(req: ChatRequest) -> Dict[str, str]:  # pragma: no cover - trivial
    return {"reply": f"Echo: {req.message}"}
