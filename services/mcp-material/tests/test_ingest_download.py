from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_upload_and_download(tmp_path):
    pid = "t1"
    content = b"hello world"
    r = client.post("/ingest/upload", params={"project_id": pid}, files={"file": ("spec.pdf", content, "application/pdf")})
    assert r.status_code == 200, r.text
    uri = r.json().get("uri")
    assert uri == f"resource://project/{pid}/files/spec.pdf"
    r2 = client.get(f"/download/{pid}/files/spec.pdf")
    assert r2.status_code == 200
    assert r2.content == content
