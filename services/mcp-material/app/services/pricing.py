from __future__ import annotations
from typing import List, Optional, Tuple
from app.schemas.bom import BOM, BOMItem, PricedBOM, PricedItem, Gap
from app.services.pricebook import Pricebook, PriceRecord
from loguru import logger

ALLOWED_UNITS = {"m","m2","m3","pcs","kg","t"}

def _unit_compatible(item_unit: Optional[str], price_unit: Optional[str]) -> bool:
    if not item_unit or not price_unit:
        return True
    return item_unit == price_unit

def price_bom(bom: BOM, region: str, date: Optional[str] = None) -> PricedBOM:
    pb = Pricebook(region=region)
    # pb.load() happens lazily in getters
    priced_items: List[PricedItem] = []
    gaps: List[Gap] = []
    subtotal = 0.0

    for it in bom.items:
        # sanity: unit
        if it.unit and it.unit not in ALLOWED_UNITS:
            gaps.append(Gap(reason="unit_mismatch", item=it, detail=f"Unsupported unit: {it.unit}"))
            continue

        rec: Optional[PriceRecord] = None
        reason: Optional[str] = None

        # 1) try by code
        if it.code:
            rec = pb.get_by_code(it.code)
            if rec is None:
                reason = "not_mapped"

        # 2) fallback by name (exact lower match)
        if rec is None and it.name:
            rec = pb.get_by_name(it.name)
            if rec is None and reason is None:
                reason = "no_price"

        if rec is None:
            gaps.append(Gap(reason=reason or "no_price", item=it, detail="No price found in pricebook"))
            continue

        # 3) unit compatibility
        if not _unit_compatible(it.unit, rec.unit):
            gaps.append(Gap(reason="unit_mismatch", item=it, detail=f"Item unit={it.unit} vs price unit={rec.unit}"))
            continue

        qty = float(it.qty or 0.0)
        unit_price = float(rec.unit_price)
        line_total = qty * unit_price
        subtotal += line_total

        priced_items.append(PricedItem(
            code=it.code or rec.code,
            name=it.name or rec.name,
            unit=it.unit or rec.unit,
            qty=qty,
            props=it.props,
            source=it.source or rec.source,
            unit_price=unit_price,
            currency=rec.currency,
            price_source=rec.source,
            lead_time_days=rec.lead_time_days,
        ))

    return PricedBOM(items=priced_items, subtotal=round(subtotal, 2), currency="EUR", gaps=gaps)
