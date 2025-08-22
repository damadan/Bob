from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_run():
    r = client.post("/run", json={"steps": []})
    assert r.status_code == 200
    assert "steps" in r.json()


def test_run_multipart():
    r = client.post("/run_multipart", files={"file": ("test.txt", b"hello", "text/plain")})
    assert r.status_code == 200
    assert r.json()["filename"] == "test.txt"


def test_chat():
    r = client.post("/chat", json={"message": "hi"})
    assert r.status_code == 200
    assert "reply" in r.json()
