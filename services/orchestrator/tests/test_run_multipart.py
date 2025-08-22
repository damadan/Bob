from fastapi.testclient import TestClient
from app.server import app
import io

def test_run_multipart_smoke():
    c = TestClient(app)
    f = io.BytesIO(b"%PDF-1.4\n%demo")
    files = {"file": ("spec.pdf", f, "application/pdf")}
    r = c.post("/run_multipart", data={"project_id": "demo"}, files=files)
    assert r.status_code in (200, 400, 422)
