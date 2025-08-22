"""Run evaluation cases through the service endpoints."""
from __future__ import annotations

from typing import List, Dict, Any
from fastapi.testclient import TestClient

from .dataset import EvalCase
from app.main import app


def run_case(client: TestClient, case: EvalCase) -> Dict[str, Any]:
    """Execute service pipeline for a single case.

    Returns a dictionary with ``case_id`` and ``priced_bom`` obtained from
    the API calls.
    """

    r = client.post("/mcp/material/parse_drawing", json={"file_uri": case.file_uri})
    r.raise_for_status()
    specs = r.json().get("specs", [])

    bom_items = []
    for s in specs:
        name = s.get("name")
        unit = s.get("unit")
        qty = s.get("qty")
        if not name or unit is None or qty is None:
            continue
        bom_items.append({"name": name, "unit": unit, "qty": qty})

    r2 = client.post(
        "/mcp/material/price_bom",
        json={"bom": {"items": bom_items}, "region": "EU-Central"},
    )
    r2.raise_for_status()
    priced_bom = r2.json()
    return {"case_id": case.id, "priced_bom": priced_bom}


def run_cases(cases: List[EvalCase], client: TestClient | None = None) -> List[Dict[str, Any]]:
    client = client or TestClient(app)
    results = []
    for case in cases:
        results.append(run_case(client, case))
    return results
