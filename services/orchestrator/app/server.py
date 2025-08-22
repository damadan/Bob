from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, Optional

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from .config import settings
from .graph import build_graph, OrchestratorError
from .state import PipelineState
from .client import mcp_client

app = FastAPI(title="MCP Orchestrator", version="0.0.1")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

graph = build_graph()


class RunRequest(BaseModel):
    project_id: str
    file_uri: str
    region: Optional[str] = None


class RunResponse(BaseModel):
    project_id: str
    export_json_url: Optional[str] = None
    export_xlsx_url: Optional[str] = None
    report_pdf_url: Optional[str] = None
    priced: Optional[Dict[str, Any]] = None


@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok"}


def _artifact_url(project_id: str, path: Optional[str]) -> Optional[str]:
    if not path:
        return None
    base = str(settings.MCP_BASE_URL).rstrip("/")
    name = os.path.basename(path)
    return f"{base}/mcp/material/download/{project_id}/outputs/{name}"


def _execute(req: RunRequest) -> RunResponse:
    state = PipelineState(
        project_id=req.project_id,
        file_uri=req.file_uri,
        region=req.region or settings.MCP_REGION,
    )
    try:
        result = graph.invoke(state)
    except OrchestratorError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return RunResponse(
        project_id=req.project_id,
        export_json_url=_artifact_url(req.project_id, result.export_json_path),
        export_xlsx_url=_artifact_url(req.project_id, result.export_xlsx_path),
        report_pdf_url=_artifact_url(req.project_id, result.report_pdf_path),
        priced=result.priced,
    )


@app.post("/run", response_model=RunResponse)
def run(req: RunRequest) -> RunResponse:
    return _execute(req)


@app.post("/run_multipart", response_model=RunResponse)
async def run_multipart(
    project_id: str = Form(...),
    file: UploadFile = File(...),
    region: Optional[str] = Form(None),
) -> RunResponse:
    content = await file.read()
    files = {"file": (file.filename, content, file.content_type or "application/octet-stream")}
    try:
        with mcp_client() as c:
            resp = c.post("/mcp/material/ingest/upload", params={"project_id": project_id}, files=files)
            resp.raise_for_status()
            payload = resp.json()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"upload failed: {e}")

    file_uri = payload.get("uri") or payload.get("file_uri")
    if not file_uri:
        raise HTTPException(status_code=400, detail="missing file uri")

    req = RunRequest(project_id=project_id, file_uri=file_uri, region=region)
    return _execute(req)


class ChatRequest(BaseModel):
    message: str


@app.post("/chat")
def chat(req: ChatRequest) -> Dict[str, str]:
    return {"reply": f"Echo: {req.message}"}


STATIC_DIR = Path(__file__).resolve().parent / "static"
app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")
