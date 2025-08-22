from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def _check(path: str):
    r = client.post(path, json={"bom": {}})
    assert r.status_code == 200
    assert "issues" in r.json()


def test_check_fire_code():
    _check("/mcp/compliance/check_fire_code")


def test_check_egress():
    _check("/mcp/compliance/check_egress")


def test_check_structural_spans():
    _check("/mcp/compliance/check_structural_spans")
