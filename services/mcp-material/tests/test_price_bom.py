from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_price_bom_basic():
    payload = {
        "bom": {
            "items": [
                {"name": "\u0411\u0435\u0442\u043e\u043d C25/30", "unit": "m3", "qty": 12.5, "code": "MAT-001"},
                {"name": "\u041a\u0438\u0440\u043f\u0438\u0447 \u041c150", "unit": "m2", "qty": 10}
            ]
        },
        "region": "EU-Central",
        "date": "2025-08-01"
    }
    r = client.post("/mcp/material/price_bom", json=payload)
    assert r.status_code == 200, r.text
    js = r.json()
    assert "items" in js and "subtotal" in js
    # at least 1 priced line
    assert any(it["code"] == "MAT-001" for it in js["items"])
    # subtotal is positive
    assert js["subtotal"] > 0

def test_price_bom_match_by_name():
    payload = {
        "bom": {"items": [{"name": "\u041a\u0438\u0440\u043f\u0438\u0447 \u041c150", "unit": "m2", "qty": 5}]},
        "region": "EU-Central"
    }
    r = client.post("/mcp/material/price_bom", json=payload)
    assert r.status_code == 200, r.text
    js = r.json()
    assert any(it["name"] == "\u041a\u0438\u0440\u043f\u0438\u0447 \u041c150" and it["unit_price"] > 0 for it in js["items"])
    assert js["subtotal"] > 0

def test_price_bom_gap_when_price_missing():
    payload = {
        "bom": {"items": [{"name": "Unknown Material", "unit": "pcs", "qty": 1}]},
        "region": "EU-Central"
    }
    r = client.post("/mcp/material/price_bom", json=payload)
    assert r.status_code == 200, r.text
    js = r.json()
    assert js["subtotal"] == 0
    assert any(g["reason"] == "no_price" for g in js.get("gaps", []))
