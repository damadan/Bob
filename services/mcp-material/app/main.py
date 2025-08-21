from fastapi import FastAPI, APIRouter, HTTPException, Response
from fastapi.responses import ORJSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from app.schemas.common import Health, Error
from app.schemas.bom import (
    BOM,
    PricedBOM,
    ParseDrawingRequest,
    ParseDrawingResponse,
    ExtractBOMRequest,
    PriceBOMRequest,
    SuggestSubsRequest,
)
from app.services.substitutions import suggest_substitutions as subs_service
from app.core.resource_uri import ResourceUriResolver
from app.parsers.pdf_parser import parse_pdf_to_specs
from app.parsers.ifc_parser import parse_ifc_to_specs
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


@app.middleware("http")
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

resolver = ResourceUriResolver()


@router.post(
    "/parse_drawing",
    response_model=ParseDrawingResponse,
    summary="Parse PDF/DWG/IFC into raw specs",
)
def parse_drawing(body: ParseDrawingRequest):
    path: Path = resolver.resolve(body.file_uri)
    if not path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        return parse_pdf_to_specs(path)
    if suffix == ".ifc":
        return parse_ifc_to_specs(path)
    # DWG (not implemented yet)
    raise HTTPException(status_code=415, detail=f"Unsupported file type: {suffix}")


@router.post(
    "/extract_bom",
    response_model=BOM,
    responses={501: {"model": Error}},
    summary="Build normalized BOM from specs/scope",
)
def extract_bom(body: ExtractBOMRequest):
    raise HTTPException(status_code=501, detail="Not implemented in step 0")


@router.post(
    "/price_bom",
    response_model=PricedBOM,
    responses={501: {"model": Error}},
    summary="Apply regional pricebook to BOM",
)
def price_bom(body: PriceBOMRequest):
    raise HTTPException(status_code=501, detail="Not implemented in step 0")


@router.post(
    "/suggest_substitutions",
    summary="Suggest alternates for gaps with constraints",
)
def suggest_substitutions(body: SuggestSubsRequest):
    region = "EU-Central"  # for MVP we can infer from context later; or pass explicitly in constraints
    payload = body.model_dump()
    return subs_service(payload, region=region)


app.include_router(router)

resolver_dbg = ResourceUriResolver()


@app.get("/resources/pricebook/{region}", tags=["debug"])
def dbg_pricebook(region: str):
    p = resolver_dbg.resolve(f"resource://pricebook/{region}")
    return Response(p.read_text(encoding="utf-8"), media_type="application/x-ndjson")


@app.get("/resources/catalog/materials", tags=["debug"])
def dbg_catalog():
    p = resolver_dbg.resolve("resource://catalog/materials")
    return Response(p.read_text(encoding="utf-8"), media_type="application/x-ndjson")
