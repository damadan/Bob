from fastapi.testclient import TestClient
from app.server import app

def test_run_missing_fields():
    c = TestClient(app)
    r = c.post("/run", json={"project_id": "demo"})
    assert r.status_code in (400, 422)
