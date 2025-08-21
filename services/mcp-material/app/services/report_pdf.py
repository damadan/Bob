from __future__ import annotations
from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from app.schemas.bom import PricedBOM
from app.core.paths import project_outputs_root, ensure_parent

def generate_priced_bom_pdf(project_id: str, priced: PricedBOM, title: str = "Сметный отчёт", filename: str | None = None) -> Path:
    out_dir = project_outputs_root(project_id)
    name = filename or "priced_bom.pdf"
    path = out_dir / name
    ensure_parent(path)

    c = canvas.Canvas(str(path), pagesize=A4)
    w, h = A4

    # Header
    c.setFont("Helvetica-Bold", 16)
    c.drawString(20*mm, (h - 20*mm), title)
    c.setFont("Helvetica", 10)
    c.drawString(20*mm, (h - 27*mm), f"Project: {project_id}")
    c.drawString(20*mm, (h - 32*mm), f"Items: {len(priced.items)}  |  Gaps: {len(priced.gaps or [])}")

    # Subtotal
    c.setFont("Helvetica-Bold", 12)
    c.drawString(20*mm, (h - 45*mm), f"Subtotal: {priced.subtotal} {priced.currency}")

    # Top items table (first 12)
    y = h - 60*mm
    c.setFont("Helvetica-Bold", 10)
    c.drawString(20*mm, y, "Позиции:")
    y -= 6*mm
    c.setFont("Helvetica", 9)
    for it in priced.items[:12]:
        line = f"- {it.name}  ({it.qty} {it.unit})  x {it.unit_price} {it.currency}"
        c.drawString(22*mm, y, line)
        y -= 5*mm
        if y < 20*mm:
            c.showPage(); y = h - 20*mm

    # Gaps (first 6)
    y -= 4*mm
    c.setFont("Helvetica-Bold", 10)
    c.drawString(20*mm, y, "Пробелы в прайсинге:")
    y -= 6*mm
    c.setFont("Helvetica", 9)
    for g in (priced.gaps or [])[:6]:
        line = f"- {g.reason}: {g.item.name} ({g.item.qty} {g.item.unit})"
        c.drawString(22*mm, y, line)
        y -= 5*mm
        if y < 20*mm:
            c.showPage(); y = h - 20*mm

    c.showPage()
    c.save()
    return path
