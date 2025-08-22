from fastapi import FastAPI, APIRouter, HTTPException, Response
from fastapi.responses import ORJSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from time import perf_counter
from fastapi import Request
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from app.core.metrics import REQUEST_LATENCY, REQUEST_COUNT
from app.schemas.common import Health, Error
from app.schemas.bom import (
    BOM,
    PricedBOM,
    ParseDrawingRequest,
    ParseDrawingResponse,
    ExtractBOMRequest,
    PriceBOMRequest,
    SuggestSubsRequest,
    ExportExcelRequest,
    ExportJsonRequest,
    ReportPdfRequest,
    MapOneRequest,
    MapOneResponse,
)
from app.services.pricing import price_bom as price_bom_service
from app.services.substitutions import (
    suggest_substitutions as subs_service,
)
from app.services.export import (
    export_excel as export_excel_service,
    export_json as export_json_service,
    report_pdf as report_pdf_service,
)
from app.services.catalog import MaterialCatalog
from app.core.resource_uri import ResourceUriResolver
from app.parsers.pdf_parser import parse_pdf_to_specs
from app.parsers.ifc_parser import parse_ifc_to_specs
from app.core.logging import setup_logging
from app.services.normalization import map_to_catalog
from app.services.quality import collect_metrics_snapshot

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
async def access_log(request: Request, call_next):
    start = perf_counter()
    method = request.method
    # truncate path to route base (no ids) for cardinality control
    path = request.url.path
    try:
        response = await call_next(request)
        status = str(response.status_code)
        return response
    except Exception as e:
        status = "500"
        logger.exception("Unhandled error")
        raise
    finally:
        dur = perf_counter() - start
        REQUEST_LATENCY.labels(method=method, path=path, status=status).observe(dur)
        REQUEST_COUNT.labels(method=method, path=path, status=status).inc()
        logger.info(f"{method} {path} -> {status} in {dur:.3f}s")


@app.get("/health", response_model=Health, tags=["health"], summary="Health check")
def health():
    return Health(status="ok", service="mcp-material", version="0.0.1")


@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

@app.get("/quality", tags=["debug"], summary="Quality metrics snapshot (JSON)")
def quality_snapshot():
    return collect_metrics_snapshot()


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
    bom = BOM()
    # after you formed a preliminary BOM named `bom`
    bom = map_to_catalog(bom, use_semantic=True)
    return bom


@router.post("/price_bom", response_model=PricedBOM, summary="Apply regional pricebook to BOM")
def price_bom(body: PriceBOMRequest):
    return price_bom_service(body.bom, body.region, body.date)


@router.post(
    "/suggest_substitutions",
    summary="Suggest alternates for gaps with constraints",
)
def suggest_substitutions(body: SuggestSubsRequest):
    region = "EU-Central"  # for MVP we can infer from context later; or pass explicitly in constraints
    payload = body.model_dump()
    return subs_service(payload, region=region)


@router.post("/export/excel")
def export_excel(body: ExportExcelRequest):
    content = export_excel_service(body.priced_bom)
    filename = body.filename or "priced_bom.xlsx"
    return Response(
        content,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.post("/export/json")
def export_json(body: ExportJsonRequest):
    content = export_json_service(body.priced_bom)
    filename = body.filename or "priced_bom.json"
    return Response(
        content,
        media_type="application/json",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.post("/report/pdf")
def report_pdf(body: ReportPdfRequest):
    content = report_pdf_service(body.priced_bom, title=body.title or "Сметный отчёт")
    filename = body.filename or "priced_bom.pdf"
    return Response(
        content,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.post("/debug/map_one", response_model=MapOneResponse)
def debug_map_one(body: MapOneRequest):
    cat = MaterialCatalog()
    cat.load()
    row = cat.best_match(body.name)
    if not row:
        return MapOneResponse()
    return MapOneResponse(code=row.code, canonical_name=row.canonical_name, score=None)


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
