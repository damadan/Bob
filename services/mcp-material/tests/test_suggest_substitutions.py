from fastapi.testclient import TestClient
from app.main import app


client = TestClient(app)


def test_returns_substitutions_for_bom_items():
    bom = {
        "items": [
            {"name": "Бетон C30", "unit": "m3", "qty": 10},
            {"name": "Кирпич М200", "unit": "m2", "qty": 100},
        ]
    }
    r = client.post("/mcp/material/suggest_substitutions", json={"bom": bom})
    assert r.status_code == 200, r.text
    js = r.json()
    assert "alternatives" in js
    assert len(js["alternatives"]) == 2
    codes = {
        alt["candidates"][0]["code"]
        for alt in js["alternatives"]
        if alt.get("candidates")
    }
    assert codes == {"MAT-001", "MAT-002"}
    for alt in js["alternatives"]:
        assert len(alt["candidates"]) <= 3

