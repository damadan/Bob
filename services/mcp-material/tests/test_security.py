from fastapi.testclient import TestClient
from app.main import app, _rate_state
from app.core import config

client = TestClient(app)


def test_disallowed_extension(tmp_path):
    content = b"data"
    r = client.post("/ingest/upload", params={"project_id": "p1"}, files={"file": ("evil.exe", content, "application/octet-stream")})
    assert r.status_code == 415


def test_oversize_file(monkeypatch):
    monkeypatch.setattr(config.settings, "MAX_FILE_SIZE_MB", 0)
    content = b"a" * 10
    r = client.post("/ingest/upload", params={"project_id": "p1"}, files={"file": ("spec.pdf", content, "application/pdf")})
    assert r.status_code == 413


def test_request_body_limit(monkeypatch):
    monkeypatch.setattr(config.settings, "MAX_REQUEST_BODY_MB", 0)
    big = "x" * 10
    r = client.post("/mcp/material/price_bom", data=big, headers={"content-type": "application/json"})
    assert r.status_code == 413


def test_api_key_required(monkeypatch):
    monkeypatch.setattr(config.settings, "API_KEY", "secret")
    r = client.post("/mcp/material/price_bom", json={"bom":{"items":[]},"region":"EU-Central"})
    assert r.status_code == 401


def test_rate_limit(monkeypatch):
    monkeypatch.setattr(config.settings, "RATE_LIMIT_RPS", 1)
    _rate_state["ts"] = 0
    client.get("/health")
    r = client.get("/health")
    assert r.status_code == 429


def test_request_timeout(monkeypatch):
    monkeypatch.setattr(config.settings, "REQUEST_TIMEOUT_SECONDS", 0)
    r = client.get("/debug/slow")
    assert r.status_code == 504
