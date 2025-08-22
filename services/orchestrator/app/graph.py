from __future__ import annotations
from typing import Callable
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from langgraph.graph import StateGraph, END
from .state import PipelineState
from .client import mcp_client
from .config import settings
import orjson
import os

class OrchestratorError(Exception): ...

def _post_json(client, path: str, payload: dict):
    r = client.post(path, json=payload)
    if r.status_code >= 400:
        raise OrchestratorError(f"{path} -> {r.status_code}: {r.text}")
    return r.json()

def _save_path_from_content_disposition(resp):
    cd = resp.headers.get("content-disposition","")
    # Content-Disposition: attachment; filename="priced_bom.json"
    name = "output.bin"
    if "filename=" in cd:
        name = cd.split("filename=",1)[1].strip('"')
    return name

@retry(stop=stop_after_attempt(settings.RETRIES), wait=wait_exponential(multiplier=0.5, min=0.5, max=4),
       retry=retry_if_exception_type(OrchestratorError))
def node_parse(state: PipelineState) -> PipelineState:
    with mcp_client() as c:
        js = _post_json(c, "/mcp/material/parse_drawing", {"file_uri": state.file_uri})
        state.parsed = js
        return state

@retry(stop=stop_after_attempt(settings.RETRIES), wait=wait_exponential(multiplier=0.5, min=0.5, max=4),
       retry=retry_if_exception_type(OrchestratorError))
def node_extract(state: PipelineState) -> PipelineState:
    # допускаем два режима: если бек уже реализует extract_bom из parsed,
    # либо принимаем упрощённый вариант: брать все specs как BOM.items
    if state.parsed and "specs" in state.parsed:
        payload = {"scope": {"specs": state.parsed["specs"]}}
    else:
        payload = {"scope": {}}
    with mcp_client() as c:
        js = _post_json(c, "/mcp/material/extract_bom", payload)
        state.bom = js
        return state

@retry(stop=stop_after_attempt(settings.RETRIES), wait=wait_exponential(multiplier=0.5, min=0.5, max=4),
       retry=retry_if_exception_type(OrchestratorError))
def node_price(state: PipelineState) -> PipelineState:
    if not state.bom:
        raise OrchestratorError("BOM is empty")
    with mcp_client() as c:
        js = _post_json(c, "/mcp/material/price_bom", {"bom": state.bom, "region": state.region})
        state.priced = js
        return state

@retry(stop=stop_after_attempt(settings.RETRIES), wait=wait_exponential(multiplier=0.5, min=0.5, max=4),
       retry=retry_if_exception_type(OrchestratorError))
def node_subs(state: PipelineState) -> PipelineState:
    if not state.priced:
        return state
    with mcp_client() as c:
        js = _post_json(c, "/mcp/material/suggest_substitutions", {
            "priced_bom": state.priced,
            "constraints": {"budget": "low"}
        })
        state.subs = js
        return state

@retry(stop=stop_after_attempt(settings.RETRIES), wait=wait_exponential(multiplier=0.5, min=0.5, max=4),
       retry=retry_if_exception_type(OrchestratorError))
def node_export(state: PipelineState) -> PipelineState:
    if not state.priced:
        return state
    with mcp_client() as c:
        # JSON
        r = c.post("/mcp/material/export/json", json={"project_id": state.project_id, "priced_bom": state.priced})
        r.raise_for_status()
        name = _save_path_from_content_disposition(r)
        state.export_json_path = f"data/projects/{state.project_id}/outputs/{name}"

        # Excel
        r2 = c.post("/mcp/material/export/excel", json={"project_id": state.project_id, "priced_bom": state.priced})
        r2.raise_for_status()
        name2 = _save_path_from_content_disposition(r2)
        state.export_xlsx_path = f"data/projects/{state.project_id}/outputs/{name2}"

        # PDF
        r3 = c.post("/mcp/material/report/pdf", json={"project_id": state.project_id, "priced_bom": state.priced, "title": "Сметный отчёт"})
        r3.raise_for_status()
        name3 = _save_path_from_content_disposition(r3)
        state.report_pdf_path = f"data/projects/{state.project_id}/outputs/{name3}"

        return state

def build_graph():
    g = StateGraph(PipelineState)
    g.add_node("parse", node_parse)
    g.add_node("extract", node_extract)
    g.add_node("price", node_price)
    g.add_node("subs", node_subs)
    g.add_node("export", node_export)

    g.set_entry_point("parse")
    g.add_edge("parse", "extract")
    g.add_edge("extract", "price")
    g.add_edge("price", "subs")
    g.add_edge("subs", "export")
    g.add_edge("export", END)

    return g.compile()
