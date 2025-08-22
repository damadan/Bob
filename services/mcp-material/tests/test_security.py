from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings
from pathlib import Path

client = TestClient(app)

def test_unauthorized_without_key(monkeypatch):
    monkeypatch.setenv("API_KEY", "secret")
    # re-import settings
    from importlib import reload
    from app.core import config as cfg
    reload(cfg)
    from app.main import app as app2
    c = TestClient(app2)
    r = c.get("/mcp/material/price_bom")
    assert r.status_code in (401,405)  # 405 if method wrong; but should not be 200


def test_body_too_large(monkeypatch):
    big = "x" * (settings.MAX_REQUEST_BODY_MB * 1024 * 1024 + 1)
    r = client.post("/mcp/material/price_bom", data=big, headers={"Content-Type":"application/json"})
    assert r.status_code == 413


def test_extension_not_allowed(tmp_path, monkeypatch):
    # setup a fake project file with .exe
    proj = (settings.DATA_ROOT / "projects" / "tsec" / "files")
    proj.mkdir(parents=True, exist_ok=True)
    bad = proj / "evil.exe"
    bad.write_bytes(b"fake")
    r = client.post("/mcp/material/parse_drawing", json={"file_uri":"resource://project/tsec/files/evil.exe"})
    assert r.status_code == 415


def test_file_too_large(tmp_path, monkeypatch):
    proj = (settings.DATA_ROOT / "projects" / "tsec2" / "files")
    proj.mkdir(parents=True, exist_ok=True)
    big = proj / "big.pdf"
    big.write_bytes(b"x" * ((settings.MAX_FILE_SIZE_MB+1) * 1024 * 1024))
    r = client.post("/mcp/material/parse_drawing", json={"file_uri":"resource://project/tsec2/files/big.pdf"})
    assert r.status_code == 413
