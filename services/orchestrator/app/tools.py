from __future__ import annotations
from typing import Optional, Dict, Any
from langchain.tools import StructuredTool
from pydantic import BaseModel, Field
from .client import mcp_client
from .config import settings

class ParseInput(BaseModel):
    file_uri: str = Field(..., description="resource://project/<id>/files/<file.pdf|.ifc>")

class ExtractInput(BaseModel):
    scope: Optional[Dict[str, Any]] = None

class PriceInput(BaseModel):
    bom: Dict[str, Any]
    region: str = settings.MCP_REGION

class SubsInput(BaseModel):
    priced_bom: Dict[str, Any]
    budget: Optional[str] = "low"

class ExportInput(BaseModel):
    project_id: str
    priced_bom: Dict[str, Any]
    filename_prefix: Optional[str] = None

def _post(path: str, payload: dict) -> Dict[str, Any]:
    with mcp_client() as c:
        r = c.post(path, json=payload)
        r.raise_for_status()
        try:
            return r.json()
        except Exception:
            return {"ok": True}

def t_parse(file_uri: str) -> Dict[str, Any]:
    return _post("/mcp/material/parse_drawing", {"file_uri": file_uri})

def t_extract(scope: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    return _post("/mcp/material/extract_bom", {"scope": scope or {}})

def t_price(bom: Dict[str, Any], region: str = settings.MCP_REGION) -> Dict[str, Any]:
    return _post("/mcp/material/price_bom", {"bom": bom, "region": region})

def t_subs(priced_bom: Dict[str, Any], budget: Optional[str] = "low") -> Dict[str, Any]:
    return _post("/mcp/material/suggest_substitutions", {"priced_bom": priced_bom, "constraints": {"budget": budget}})

def t_export(project_id: str, priced_bom: Dict[str, Any], filename_prefix: Optional[str] = None) -> Dict[str, Any]:
    out = {}
    with mcp_client() as c:
        for kind, path in [("json","/mcp/material/export/json"),
                           ("excel","/mcp/material/export/excel"),
                           ("pdf","/mcp/material/report/pdf")]:
            payload = {"project_id": project_id, "priced_bom": priced_bom}
            if filename_prefix:
                payload["filename"] = f"{filename_prefix}.{ 'json' if kind=='json' else ('xlsx' if kind=='excel' else 'pdf') }"
            r = c.post(path, json=payload); r.raise_for_status()
            cd = r.headers.get("content-disposition","")
            name = "output"
            if "filename=" in cd:
                name = cd.split("filename=",1)[1].strip('"')
            out[kind] = f"data/projects/{project_id}/outputs/{name}"
    return out

parse_tool = StructuredTool.from_function(name="parse_drawing", description="Parse PDF/IFC into raw specs", func=t_parse, args_schema=ParseInput)
extract_tool = StructuredTool.from_function(name="extract_bom", description="Normalize/build BOM from parsed scope", func=lambda scope=None: t_extract(scope), args_schema=ExtractInput)
price_tool = StructuredTool.from_function(name="price_bom", description="Apply regional pricebook to BOM", func=lambda bom, region=settings.MCP_REGION: t_price(bom, region), args_schema=PriceInput)
subs_tool = StructuredTool.from_function(name="suggest_substitutions", description="Suggest material alternatives for gaps", func=lambda priced_bom, budget="low": t_subs(priced_bom, budget), args_schema=SubsInput)
export_tool = StructuredTool.from_function(name="export_results", description="Export PricedBOM to JSON/XLSX/PDF", func=lambda project_id, priced_bom, filename_prefix=None: t_export(project_id, priced_bom, filename_prefix), args_schema=ExportInput)
