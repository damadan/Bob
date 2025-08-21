from __future__ import annotations
from pathlib import Path
from typing import Tuple
import json
import pandas as pd
from app.schemas.bom import PricedBOM
from app.core.paths import project_outputs_root, ensure_parent

def export_priced_bom_excel(project_id: str, priced: PricedBOM, filename: str | None = None) -> Path:
    out_dir = project_outputs_root(project_id)
    name = filename or "priced_bom.xlsx"
    path = out_dir / name

    rows = []
    for it in priced.items:
        rows.append({
            "code": it.code,
            "name": it.name,
            "unit": it.unit,
            "qty": it.qty,
            "unit_price": it.unit_price,
            "currency": it.currency,
            "lead_time_days": it.lead_time_days,
            "price_source": it.price_source,
        })
    df_items = pd.DataFrame(rows)

    gaps = []
    for g in (priced.gaps or []):
        gaps.append({
            "reason": g.reason,
            "item_name": g.item.name,
            "item_unit": g.item.unit,
            "item_qty": g.item.qty,
            "detail": g.detail,
        })
    df_gaps = pd.DataFrame(gaps)

    ensure_parent(path)
    with pd.ExcelWriter(path) as xw:
        df_items.to_excel(xw, index=False, sheet_name="Items")
        df_gaps.to_excel(xw, index=False, sheet_name="Gaps")
        # Summary sheet
        pd.DataFrame([{
            "subtotal": priced.subtotal,
            "currency": priced.currency,
            "items_count": len(priced.items),
            "gaps_count": len(priced.gaps or []),
        }]).to_excel(xw, index=False, sheet_name="Summary")
    return path


def export_priced_bom_json(project_id: str, priced: PricedBOM, filename: str | None = None) -> Path:
    out_dir = project_outputs_root(project_id)
    name = filename or "priced_bom.json"
    path = out_dir / name
    ensure_parent(path)
    path.write_text(json.dumps(priced.model_dump(), ensure_ascii=False, indent=2), encoding="utf-8")
    return path
