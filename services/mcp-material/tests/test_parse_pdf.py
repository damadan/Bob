import io
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from fastapi.testclient import TestClient
from pathlib import Path
from app.main import app
from app.core.config import settings

client = TestClient(app)

def _make_pdf_table(tmp_path: Path) -> Path:
    p = tmp_path / "spec.pdf"
    buf = io.BytesIO()
    c = canvas.Canvas(str(p), pagesize=A4)
    # simple text table imitation
    y = 800
    rows = [
        ["Наименование", "Ед. изм", "Кол-во", "Марка"],
        ["Бетон C25/30", "м3", "12,5", ""],
        ["Дверь ДГ-21", "шт", "10", "ДГ-21"],
    ]
    for r in rows:
        x = 50
        for cell in r:
            c.drawString(x, y, cell)
            x += 150
        y -= 20
    c.showPage()
    c.save()
    return p

def test_parse_pdf(tmp_path, monkeypatch):
    # prepare resource:// path
    proj = settings.DATA_ROOT / "projects" / "t1" / "files"
    proj.mkdir(parents=True, exist_ok=True)
    pdf_path = _make_pdf_table(tmp_path)
    target = proj / "spec.pdf"
    target.write_bytes(pdf_path.read_bytes())

    r = client.post("/mcp/material/parse_drawing", json={"file_uri": "resource://project/t1/files/spec.pdf"})
    assert r.status_code == 200, r.text
    js = r.json()
    assert "specs" in js and isinstance(js["specs"], list)
    # should extract at least 1 spec row
    assert len(js["specs"]) >= 1
