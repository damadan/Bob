from fastapi.testclient import TestClient
import pytest

from app.main import app


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def tiny_pdf() -> bytes:
    """Return bytes for a minimal PDF file."""
    return b"%PDF-1.1\n1 0 obj\n<<>>\nendobj\ntrailer\n<<>>\n%%EOF\n"

