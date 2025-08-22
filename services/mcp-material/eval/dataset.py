"""Evaluation dataset loader for mcp-material service."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict, Any
import json

from app.core.config import settings


@dataclass
class EvalCase:
    """Single evaluation case.

    Attributes:
        id: Case identifier used as project id.
        file_uri: resource:// URI to the input document.
        expected_items: List of expected BOM items with name/unit/qty.
    """

    id: str
    file_uri: str
    expected_items: List[Dict[str, Any]]


_DEF_DATA_PATH = Path(__file__).parent / "data"


def load_dataset(path: Path | None = None) -> List[EvalCase]:
    """Load evaluation cases from JSON file.

    The JSON is expected to have entries with ``id``, ``file`` (relative
    to ``data/files``) and ``expected_items``. Files are copied into the
    service ``DATA_ROOT`` so that they can be accessed via ``resource://``
    URIs when calling the API.
    """

    base = path or _DEF_DATA_PATH
    data_file = base / "cases.json"
    raw_cases = json.loads(data_file.read_text(encoding="utf-8"))
    cases: List[EvalCase] = []
    for c in raw_cases:
        cid = c["id"]
        fname = c["file"]
        src = base / "files" / fname
        # Place file under DATA_ROOT/projects/<id>/files
        dst = settings.DATA_ROOT / "projects" / cid / "files" / fname
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_bytes(src.read_bytes())
        file_uri = f"resource://project/{cid}/files/{fname}"
        cases.append(EvalCase(id=cid, file_uri=file_uri, expected_items=c["expected_items"]))
    return cases
