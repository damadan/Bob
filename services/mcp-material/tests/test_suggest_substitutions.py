from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_suggest_substitutions_no_constraint():
    r = client.post("/mcp/material/suggest_substitutions", json={})
    assert r.status_code == 200, r.text
    js = r.json()
    codes = [c["code"] for c in js["candidates"]]
    assert "MAT-003" in codes


def test_suggest_substitutions_with_lead_time():
    r = client.post(
        "/mcp/material/suggest_substitutions",
        json={"constraints": {"lead_time": "<=30d"}},
    )
    assert r.status_code == 200, r.text
    js = r.json()
    assert all(
        c.get("lead_time_days") is None or c["lead_time_days"] <= 30
        for c in js["candidates"]
    )
    codes = [c["code"] for c in js["candidates"]]
    assert "MAT-003" not in codes
