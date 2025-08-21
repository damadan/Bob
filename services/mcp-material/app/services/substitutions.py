from __future__ import annotations
from typing import Dict, Any, List
from app.schemas.bom import BOM, PricedBOM, Gap
from app.services.pricebook import Pricebook
from loguru import logger


def suggest_substitutions(payload: Dict[str, Any], region: str) -> Dict[str, Any]:
    """
    Input payload may have:
      - bom: BOM (optional)
      - priced_bom: PricedBOM (optional)
      - constraints: {"budget": "low"|"mid"|"high", "lead_time": "<=30d"|None}
    Returns dict: {"alternatives": [{"for_code":..., "candidates":[...]}]}
    """
    pb = Pricebook(region=region)
    pb.load()

    bom_data = payload.get("bom")
    priced_data = payload.get("priced_bom")
    bom: BOM | None = BOM.model_validate(bom_data) if bom_data else None
    priced: PricedBOM | None = (
        PricedBOM.model_validate(priced_data) if priced_data else None
    )
    constraints: Dict[str, Any] = payload.get("constraints") or {}

    # choose gaps to cover
    targets = []
    if priced and priced.gaps:
        for g in priced.gaps:
            targets.append(g.item)
    elif bom:
        targets = bom.items
    else:
        return {"alternatives": []}

    results: List[Dict[str, Any]] = []
    price_list = [pb.get_by_code(c) for c in pb.codes()]
    price_list = [p for p in price_list if p]

    for it in targets:
        canon = (it.name or "").lower()
        cls = (it.props or {}).get("class")
        # candidate filter
        cand = []
        for r in price_list:
            rname = (r.name or "").lower()
            if cls and cls in rname:
                cand.append(r)
            elif canon and canon.split()[0] in rname:
                cand.append(r)
        # constraints
        budget = (constraints.get("budget") or "").lower()
        if budget == "low":
            cand = sorted(cand, key=lambda x: x.unit_price)
        else:
            cand = sorted(cand, key=lambda x: (x.lead_time_days or 9999, x.unit_price))

        cand = cand[:3]
        results.append({
            "for_item": it.model_dump(),
            "candidates": [
                {
                    "code": r.code, "name": r.name, "unit": r.unit,
                    "unit_price": r.unit_price, "currency": r.currency,
                    "lead_time_days": r.lead_time_days, "source": r.source
                } for r in cand
            ]
        })

    return {"alternatives": results}

