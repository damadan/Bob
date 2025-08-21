from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def _call(budget: str):
    payload = {"constraints": {"budget": budget}}
    return client.post("/mcp/material/suggest_substitutions", json=payload)


def test_low_budget_returns_cheapest_first():
    r = _call("low")
    assert r.status_code == 200, r.text
    js = r.json()
    prices = [s["unit_price"] for s in js["suggestions"]]
    # low budget keeps all items sorted ascending, so the first is the cheapest
    assert prices == sorted(prices)
    assert prices[0] == 10


def test_mid_budget_filters_extremes_and_sorts_ascending():
    r = _call("mid")
    assert r.status_code == 200, r.text
    js = r.json()
    prices = [s["unit_price"] for s in js["suggestions"]]
    # mid budget should drop the very cheap and very expensive options
    assert prices == [100, 200]


def test_high_budget_prefers_expensive_sorted_desc():
    r = _call("high")
    assert r.status_code == 200, r.text
    js = r.json()
    prices = [s["unit_price"] for s in js["suggestions"]]
    # high budget returns expensive items first
    assert prices == [1000, 200]
