from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

SAMPLE_PRICED = {
    "items": [
        {"name":"Бетон C25/30","unit":"m3","qty":12.5,"code":"MAT-001","unit_price":95.4,"currency":"EUR"},
        {"name":"Кирпич М150","unit":"m2","qty":10.0,"code":"MAT-002","unit_price":12.1,"currency":"EUR"},
    ],
    "subtotal": 95.4*12.5 + 12.1*10.0,
    "currency": "EUR",
    "gaps": []
}

def test_export_excel(tmp_path, monkeypatch):
    payload = {"project_id":"t1","priced_bom":SAMPLE_PRICED}
    r = client.post("/mcp/material/export/excel", json=payload)
    assert r.status_code == 200, r.text
    assert "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" in r.headers.get("content-type","")

def test_export_json(tmp_path, monkeypatch):
    payload = {"project_id":"t1","priced_bom":SAMPLE_PRICED}
    r = client.post("/mcp/material/export/json", json=payload)
    assert r.status_code == 200, r.text
    assert "application/json" in r.headers.get("content-type","")

def test_report_pdf(tmp_path, monkeypatch):
    payload = {"project_id":"t1","priced_bom":SAMPLE_PRICED, "title":"Отчёт (тест)"}
    r = client.post("/mcp/material/report/pdf", json=payload)
    assert r.status_code == 200, r.text
    assert "application/pdf" in r.headers.get("content-type","")
