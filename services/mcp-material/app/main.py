from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import ORJSONResponse
from typing import Optional, Dict, Any
from app.schemas.common import Health, Error
from app.schemas.bom import BOM, PricedBOM
from app.core.logging import setup_logging
from app.core.config import settings

logger = setup_logging()

app = FastAPI(
    title="MCP Material Takeoff & Costing",
    version="0.0.1",
    default_response_class=ORJSONResponse,
)


@app.get("/health", response_model=Health, tags=["health"])
def health():
    return Health(status="ok", service="mcp-material", version="0.0.1")


@app.post("/parse_drawing", tags=["mcp"], responses={501: {"model": Error}})
def parse_drawing(
    file_uri: str = Query(..., description="resource://project/<id>/files/<file>"),
) -> Dict[str, Any]:
    # Шаг 1–2 реализуем позже
    raise HTTPException(status_code=501, detail="Not implemented in step 0")


@app.post("/extract_bom", response_model=BOM, tags=["mcp"], responses={501: {"model": Error}})
def extract_bom(scope: Dict[str, Any]) -> BOM:
    raise HTTPException(status_code=501, detail="Not implemented in step 0")


@app.post("/price_bom", response_model=PricedBOM, tags=["mcp"], responses={501: {"model": Error}})
def price_bom(payload: Dict[str, Any]) -> PricedBOM:
    raise HTTPException(status_code=501, detail="Not implemented in step 0")


@app.post("/suggest_substitutions", tags=["mcp"], responses={501: {"model": Error}})
def suggest_substitutions(payload: Dict[str, Any]) -> Dict[str, Any]:
    raise HTTPException(status_code=501, detail="Not implemented in step 0")
