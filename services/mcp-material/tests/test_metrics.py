from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_metrics_endpoint():
    r = client.get("/metrics")
    assert r.status_code == 200
    assert "http_request_duration_seconds" in r.text


def test_quality_snapshot():
    r = client.get("/quality")
    assert r.status_code == 200
    assert isinstance(r.json(), dict)
