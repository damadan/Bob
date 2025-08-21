from __future__ import annotations
from typing import Dict, Any, List, Optional
from dataclasses import asdict
from app.services.pricebook import Pricebook, PriceRecord


def _parse_lead_time(value: Any) -> Optional[int]:
    if value is None:
        return None
    if isinstance(value, int):
        return value
    if not isinstance(value, str):
        return None
    s = value.strip()
    if s.startswith("<="):
        s = s[2:]
    if s.endswith("d"):
        s = s[:-1]
    try:
        return int(s)
    except ValueError:
        return None


def suggest_substitutions(
    region: str, constraints: Optional[Dict[str, Any]] = None
) -> List[Dict[str, Any]]:
    pb = Pricebook(region=region)
    candidates: List[PriceRecord] = []
    for code in pb.codes():
        rec = pb.get_by_code(code)
        if rec:
            candidates.append(rec)
    # sort candidates by unit price then code for determinism
    candidates.sort(key=lambda r: (r.unit_price, r.code))

    limit = None
    if constraints:
        limit = _parse_lead_time(constraints.get("lead_time"))
    if limit is not None:
        candidates = [c for c in candidates if c.lead_time_days is None or c.lead_time_days <= limit]

    return [asdict(c) for c in candidates]
