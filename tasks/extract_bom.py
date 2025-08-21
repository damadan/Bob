"""
Implement extract_bom endpoint:
- Input: RawSpec (list of tables with headers, rows)
- Output: List[BOMItem]

Steps:
1. Flatten all tables into one list of rows.
2. Auto-detect header mapping (e.g., "Наименование" -> name, "Кол-во" -> quantity).
3. Clean and normalize:
   - skip empty/misc rows
   - unify units (use unit_map = {"м2":"sqm", "м3":"m3", "шт":"pcs"})
   - parse quantity as float
4. Deduplicate by (name+unit), summing quantities.
5. Return list of BOMItem objects.
"""

from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Dict, Tuple

try:  # pragma: no cover - optional import for integration
    from app.schemas.bom import BOMItem  # type: ignore
except Exception:  # pragma: no cover - fallback simple model
    class BOMItem(BaseModel):
        name: str
        unit: str
        qty: float


class RawTable(BaseModel):
    headers: List[str]
    rows: List[List[str]]


class RawSpec(BaseModel):
    tables: List[RawTable]


router = APIRouter()

# Mapping of common header names to canonical keys
_HEADER_ALIASES: Dict[str, str] = {
    "наименование": "name",
    "название": "name",
    "наим": "name",
    "ед": "unit",
    "ед. изм": "unit",
    "ед изм": "unit",
    "unit": "unit",
    "кол": "quantity",
    "количество": "quantity",
    "кол-во": "quantity",
    "qty": "quantity",
    "объем": "quantity",
    "объём": "quantity",
}

# Unit normalization map
_UNIT_MAP = {"м2": "sqm", "м3": "m3", "шт": "pcs"}


def _map_headers(headers: List[str]) -> Dict[str, int]:
    """Return mapping of canonical field -> column index."""
    mapping: Dict[str, int] = {}
    for idx, h in enumerate(headers):
        key = _HEADER_ALIASES.get(h.strip().lower())
        if key and key not in mapping:
            mapping[key] = idx
    return mapping


def _parse_quantity(val) -> float | None:
    try:
        if isinstance(val, (int, float)):
            return float(val)
        s = str(val).strip().replace(" ", "").replace(",", ".")
        return float(s)
    except Exception:  # pragma: no cover - invalid values
        return None


@router.post("/mcp/material/extract_bom", response_model=List[BOMItem])
def extract_bom(spec: RawSpec) -> List[BOMItem]:
    """Build a normalized BOM list from raw tables."""
    aggregated: Dict[Tuple[str, str], float] = {}

    for table in spec.tables or []:
        hmap = _map_headers(table.headers or [])
        idx_name = hmap.get("name")
        idx_unit = hmap.get("unit")
        idx_qty = hmap.get("quantity")

        for row in table.rows or []:
            name = (
                str(row[idx_name]).strip()
                if idx_name is not None and idx_name < len(row)
                else ""
            )
            if not name:
                continue

            unit = (
                str(row[idx_unit]).strip().lower()
                if idx_unit is not None and idx_unit < len(row)
                else ""
            )
            unit = _UNIT_MAP.get(unit, unit)

            qty_val = (
                row[idx_qty] if idx_qty is not None and idx_qty < len(row) else None
            )
            qty = _parse_quantity(qty_val)
            if qty is None:
                continue

            key = (name.lower(), unit)
            aggregated[key] = aggregated.get(key, 0.0) + qty

    items = [BOMItem(name=k[0], unit=k[1], qty=v) for k, v in aggregated.items()]
    return items
