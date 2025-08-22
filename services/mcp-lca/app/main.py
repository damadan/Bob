from fastapi import FastAPI
from pydantic import BaseModel
from typing import Dict

app = FastAPI(title="MCP LCA", version="0.0.1")


class LCARequest(BaseModel):
    bom: Dict = {}


class CompareRequest(BaseModel):
    option_a: Dict = {}
    option_b: Dict = {}


@app.get("/health")
async def health() -> Dict[str, str]:
    return {"status": "ok"}


@app.post("/mcp/lca/estimate")
async def estimate(_: LCARequest) -> Dict[str, int]:  # pragma: no cover - trivial
    return {"embodied_carbon": 0}


@app.post("/mcp/lca/compare")
async def compare(_: CompareRequest) -> Dict[str, str]:  # pragma: no cover - trivial
    return {"better_option": "option_a"}
