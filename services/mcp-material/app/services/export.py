from __future__ import annotations

from io import BytesIO
import json
import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

from app.schemas.bom import PricedBOM


def export_excel(priced_bom: PricedBOM) -> bytes:
    df = pd.DataFrame([item.model_dump() for item in priced_bom.items])
    buf = BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        df.to_excel(writer, index=False)
    return buf.getvalue()


def export_json(priced_bom: PricedBOM) -> bytes:
    return json.dumps(priced_bom.model_dump(), ensure_ascii=False).encode("utf-8")


def report_pdf(priced_bom: PricedBOM, title: str) -> bytes:
    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    width, height = A4
    y = height - 40
    c.setFont("Helvetica", 14)
    c.drawString(40, y, title)
    c.setFont("Helvetica", 10)
    y -= 30
    for it in priced_bom.items:
        line = f"{it.name} ({it.unit}): {it.qty} x {it.unit_price} {it.currency}"
        c.drawString(40, y, line)
        y -= 15
        if y < 40:
            c.showPage()
            c.setFont("Helvetica", 10)
            y = height - 40
    c.save()
    return buf.getvalue()
