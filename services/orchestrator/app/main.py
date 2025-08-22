from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
from typing import List, Dict

app = FastAPI(title="MCP Orchestrator", version="0.0.1")


class RunRequest(BaseModel):
    steps: List[Dict] = []


class ChatRequest(BaseModel):
    message: str


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
