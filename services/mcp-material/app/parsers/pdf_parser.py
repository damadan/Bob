from typing import List, Dict, Any
from pathlib import Path
import pdfplumber

try:
    import camelot  # optional

    HAS_CAMEL0T = True
except Exception:
    HAS_CAMEL0T = False

from .utils import canonical_header, normalize_unit, parse_number
from app.schemas.bom import RawSpec


def _plumber_tables(pdf_path: Path) -> List[Dict[str, Any]]:
    tables_out: List[Dict[str, Any]] = []
    with pdfplumber.open(pdf_path) as pdf:
        for pi, page in enumerate(pdf.pages):
            try:
                tables = page.extract_tables(
                    {
                        "vertical_strategy": "text",
                        "horizontal_strategy": "text",
                    }
                )
            except Exception:
                tables = []
            for ti, t in enumerate(tables or []):
                if not t or len(t) < 2:
                    continue
                headers = [canonical_header((h or "").strip()) for h in t[0]]
                rows = t[1:]
                tables_out.append(
                    {
                        "page": pi + 1,
                        "name": f"pdfplumber_p{pi+1}_t{ti+1}",
                        "headers": headers,
                        "rows": rows,
                        "engine": "pdfplumber",
                    }
                )
    return tables_out


def _camelot_tables(pdf_path: Path) -> List[Dict[str, Any]]:
    if not HAS_CAMEL0T:
        return []
    try:
        tables = camelot.read_pdf(str(pdf_path), flavor="lattice", pages="all")
    except Exception:
        return []
    out = []
    for i, t in enumerate(tables):
        df = t.df
        if df is None or df.shape[0] < 2:
            continue
        headers = [canonical_header(str(x)) for x in df.iloc[0].tolist()]
        rows = df.iloc[1:].values.tolist()
        out.append(
            {
                "page": None,
                "name": f"camelot_t{i+1}",
                "headers": headers,
                "rows": rows,
                "engine": "camelot",
            }
        )
    return out


def parse_pdf_to_specs(pdf_path: Path) -> Dict[str, Any]:
    tables = _plumber_tables(pdf_path)
    # Append camelot-only tables (sometimes extracts better headers)
    camel_tables = _camelot_tables(pdf_path)
    # de-duplicate by name
    seen = {t["name"] for t in tables}
    for ct in camel_tables:
        if ct["name"] not in seen:
            tables.append(ct)

    specs: List[RawSpec] = []
    for t in tables:
        headers = t.get("headers") or []
        hidx = {h: i for i, h in enumerate(headers)}
        # try to map common fields
        idx_name = hidx.get("наименование", 0)
        idx_unit = hidx.get("ед", None)
        idx_qty = hidx.get("количество", None)
        idx_mark = hidx.get("марка", None)

        for ri, row in enumerate(t.get("rows") or []):
            try:
                name = (
                    str(row[idx_name]).strip()
                    if idx_name is not None and idx_name < len(row)
                    else ""
                )
                if not name:
                    continue
                unit = (
                    normalize_unit(str(row[idx_unit]).strip())
                    if idx_unit is not None and idx_unit < len(row)
                    else None
                )
                qty = (
                    parse_number(row[idx_qty])
                    if idx_qty is not None and idx_qty < len(row)
                    else None
                )
                mark = (
                    str(row[idx_mark]).strip()
                    if idx_mark is not None and idx_mark < len(row)
                    else None
                )
                specs.append(
                    RawSpec(
                        row_index=ri,
                        name=name,
                        unit=unit,
                        qty=qty,
                        mark=mark,
                        source_table=t["name"],
                        extras={"engine": t.get("engine"), "page": t.get("page")},
                    )
                )
            except Exception:
                # be robust: skip bad rows
                continue

    return {
        "specs": [s.model_dump() for s in specs],
        "tables": tables,
        "notes": [],
    }
