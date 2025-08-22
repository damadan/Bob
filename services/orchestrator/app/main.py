from pathlib import Path
from typing import Dict, List

from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel


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
    steps: List[Dict] = []


class ChatRequest(BaseModel):
    message: str


@app.get("/")
async def index() -> FileResponse:  # pragma: no cover - simple static file
    """Serve the minimal HTML client."""
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/health")
async def health() -> Dict[str, str]:
    return {"status": "ok"}


@app.post("/run")
async def run(req: RunRequest) -> Dict[str, List[Dict]]:  # pragma: no cover - trivial
    return {"steps": req.steps}


@app.post("/run_multipart")
async def run_multipart(file: UploadFile = File(...)) -> Dict[str, str]:
    data = await file.read()
    return {"filename": file.filename, "size": str(len(data))}


@app.post("/chat")
async def chat(req: ChatRequest) -> Dict[str, str]:  # pragma: no cover - trivial
    return {"reply": f"Echo: {req.message}"}
