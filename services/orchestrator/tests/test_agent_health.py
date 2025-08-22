from fastapi.testclient import TestClient
from app.chat_server import app

def test_health():
    c = TestClient(app)
    r = c.get("/health")
    assert r.status_code == 200
    assert "agent_ready" in r.json()
