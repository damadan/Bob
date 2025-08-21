import re
from typing import Dict, List, Tuple, Optional

HEADER_ALIASES = {
    "наименование": ["наименование", "название", "material", "item", "наим."],
    "ед": ["ед", "ед.", "ед изм", "ед. изм", "единица", "unit"],
    "количество": ["кол-во", "количество", "кол.", "qty", "объем", "объём"],
    "марка": ["марка", "тип", "артикул", "brand", "code"],
}

def canonical_header(h: str) -> str:
    s = re.sub(r"\s+", " ", h.strip().lower())
    for canon, variants in HEADER_ALIASES.items():
        if s in variants:
            return canon
    # fallback heuristics
    if "ед" in s or "unit" in s:
        return "ед"
    if "кол" in s or "qty" in s or "объем" in s or "объём" in s:
        return "количество"
    if "марка" in s or "тип" in s or "артикул" in s or "brand" in s or "code" in s:
        return "марка"
    return "наименование" if len(s) <= 3 else s

_UNIT_MAP = {
    "м2": "m2", "м³": "m3", "м3": "m3", "м": "m", "шт": "pcs", "кг": "kg", "т": "t",
    "m2": "m2", "m3": "m3", "m": "m", "pcs": "pcs", "kg": "kg", "t": "t",
}

def normalize_unit(u: Optional[str]) -> Optional[str]:
    if not u:
        return None
    s = u.strip().lower().replace("^2", "2").replace("^3", "3")
    s = s.replace(" кв.м", " м2").replace("куб.м", " м3")
    s = re.sub(r"\s+", "", s)
    return _UNIT_MAP.get(s, s)

_NUM_RE = re.compile(r"^[\s]*([+-]?[0-9]+(?:[.,][0-9]+)?)")

def parse_number(val) -> Optional[float]:
    if val is None:
        return None
    if isinstance(val, (int, float)):
        return float(val)
    s = str(val)
    m = _NUM_RE.match(s.replace(" ", ""))
    if not m:
        return None
    num = m.group(1).replace(",", ".")
    try:
        return float(num)
    except ValueError:
        return None
