from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_estimate():
    r = client.post("/mcp/lca/estimate", json={"bom": {}})
    assert r.status_code == 200
    assert "embodied_carbon" in r.json()


def test_compare():
    r = client.post(
        "/mcp/lca/compare",
        json={"option_a": {}, "option_b": {}}
    )
    assert r.status_code == 200
    assert "better_option" in r.json()
