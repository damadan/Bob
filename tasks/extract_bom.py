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
from typing import Any, Dict, List, Tuple

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

# Fuzzy header mapping lists
_HEADERS_MAP: Dict[str, List[str]] = {
    "name": ["наименование", "материал", "item"],
    "quantity": ["кол-во", "количество", "qty"],
    "unit": ["ед.", "единица", "unit"],
    "code": ["код", "артикул", "id"],
}

# Unit normalization map
_UNIT_MAP = {"м2": "sqm", "м3": "m3", "шт": "pcs"}


def _map_headers(headers: List[str]) -> Dict[str, int]:
    """Return mapping of canonical field -> column index using fuzzy match."""
    mapping: Dict[str, int] = {}
    for idx, header in enumerate(headers):
        h = header.strip().lower()
        for canon, variants in _HEADERS_MAP.items():
            if canon in mapping:
                continue
            for variant in variants:
                if variant in h:
                    mapping[canon] = idx
                    break
    return mapping


def _parse_quantity(val) -> float:
    """Parse quantity into float, returning 0.0 on failure."""
    try:
        if isinstance(val, (int, float)):
            return float(val)
        s = str(val).strip().replace(" ", "").replace(",", ".")
        return float(s)
    except Exception:  # pragma: no cover - invalid values
        return 0.0


@router.post("/mcp/material/extract_bom", response_model=List[BOMItem])
def extract_bom(spec: RawSpec) -> List[BOMItem]:
    """Build a normalized BOM list from raw tables."""

    aggregated: Dict[Tuple[str, str], Dict[str, Any]] = {}

    for table in spec.tables or []:
        hmap = _map_headers(table.headers or [])
        idx_name = hmap.get("name")
        idx_unit = hmap.get("unit")
        idx_qty = hmap.get("quantity")
        idx_code = hmap.get("code")

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

            qty_val = row[idx_qty] if idx_qty is not None and idx_qty < len(row) else None
            qty = _parse_quantity(qty_val)

            code = (
                str(row[idx_code]).strip()
                if idx_code is not None and idx_code < len(row)
                else None
            )

            item = {
                "name": name,
                "unit": unit,
                "quantity": qty,
                "code": code,
                "category": None,
            }

            key = (name.lower(), unit)
            if key in aggregated:
                aggregated[key]["quantity"] += qty
            else:
                aggregated[key] = item

    return [
        BOMItem(
            code=v.get("code"),
            name=v["name"],
            unit=v["unit"],
            qty=v["quantity"],
        )
        for v in aggregated.values()
    ]
