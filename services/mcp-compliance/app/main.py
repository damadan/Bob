from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Dict

app = FastAPI(title="MCP Compliance", version="0.0.1")


class CheckRequest(BaseModel):
    bom: Dict = {}


class IssuesResponse(BaseModel):
    issues: List[str]


@app.get("/health")
async def health() -> Dict[str, str]:
    return {"status": "ok"}


@app.post("/mcp/compliance/check_fire_code", response_model=IssuesResponse)
async def check_fire_code(_: CheckRequest) -> IssuesResponse:  # pragma: no cover - trivial
    return IssuesResponse(issues=[])


@app.post("/mcp/compliance/check_egress", response_model=IssuesResponse)
async def check_egress(_: CheckRequest) -> IssuesResponse:  # pragma: no cover - trivial
    return IssuesResponse(issues=[])


@app.post("/mcp/compliance/check_structural_spans", response_model=IssuesResponse)
async def check_structural_spans(_: CheckRequest) -> IssuesResponse:  # pragma: no cover - trivial
    return IssuesResponse(issues=[])
