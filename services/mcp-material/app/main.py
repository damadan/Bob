from fastapi import FastAPI, APIRouter, HTTPException
from fastapi.responses import ORJSONResponse
from fastapi.middleware.cors import CORSMiddleware
from app.schemas.common import Health, Error
from app.schemas.bom import (
    BOM,
    PricedBOM,
    ParseDrawingRequest,
    ExtractBOMRequest,
    PriceBOMRequest,
    SuggestSubsRequest,
)
from app.core.logging import setup_logging

logger = setup_logging()

app = FastAPI(
    title="MCP Material Takeoff & Costing",
    version="0.0.1",
    default_response_class=ORJSONResponse,
)

# CORS (relax for dev; restrict in prod)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@ app.middleware("http")
async def access_log(request, call_next):
    logger.info(f"{request.method} {request.url}")
    try:
        response = await call_next(request)
        logger.info(f"-> {response.status_code}")
        return response
    except Exception:
        logger.exception("Unhandled error")
        raise

@app.get("/health", response_model=Health, tags=["health"], summary="Health check")
def health():
    return Health(status="ok", service="mcp-material", version="0.0.1")

router = APIRouter(prefix="/mcp/material", tags=["mcp"])

@router.post("/parse_drawing", responses={501: {"model": Error}}, summary="Parse PDF/DWG/IFC into raw specs")
def parse_drawing(body: ParseDrawingRequest):
    raise HTTPException(status_code=501, detail="Not implemented in step 0")

@router.post("/extract_bom", response_model=BOM, responses={501: {"model": Error}}, summary="Build normalized BOM from specs/scope")
def extract_bom(body: ExtractBOMRequest):
    raise HTTPException(status_code=501, detail="Not implemented in step 0")

@router.post("/price_bom", response_model=PricedBOM, responses={501: {"model": Error}}, summary="Apply regional pricebook to BOM")
def price_bom(body: PriceBOMRequest):
    raise HTTPException(status_code=501, detail="Not implemented in step 0")

@router.post("/suggest_substitutions", responses={501: {"model": Error}}, summary="Suggest alternates for gaps with constraints")
def suggest_substitutions(body: SuggestSubsRequest):
    raise HTTPException(status_code=501, detail="Not implemented in step 0")

app.include_router(router)
