from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_run():
    payload = {
        "project_id": "123",
        "priced_bom": {"total": 1},
        "filenames": {
            "excel": "bom.xlsx",
            "json": "bom.json",
            "pdf": "bom.pdf",
        },
    }
    r = client.post("/run", json=payload)
    assert r.status_code == 200
    js = r.json()
    assert js["priced_bom"]["total"] == 1
    base = "http://localhost:8080"
    assert js["artifacts"]["excel_url"] == f"{base}/mcp/material/download/123/outputs/bom.xlsx"
    assert js["artifacts"]["json_url"] == f"{base}/mcp/material/download/123/outputs/bom.json"
    assert js["artifacts"]["pdf_url"] == f"{base}/mcp/material/download/123/outputs/bom.pdf"


def test_run_multipart():
    r = client.post(
        "/run_multipart",
        params={"project_id": "xyz"},
        files={"file": ("test.txt", b"hello", "text/plain")},
    )
    assert r.status_code == 200
    js = r.json()
    base = "http://localhost:8080"
    assert js["artifacts"]["excel_url"] == f"{base}/mcp/material/download/xyz/outputs/test.xlsx"
    assert js["artifacts"]["json_url"] == f"{base}/mcp/material/download/xyz/outputs/test.json"
    assert js["artifacts"]["pdf_url"] == f"{base}/mcp/material/download/xyz/outputs/test.pdf"


def test_chat():
    r = client.post("/chat", json={"message": "hi"})
    assert r.status_code == 200
    assert "reply" in r.json()
