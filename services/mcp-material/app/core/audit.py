from __future__ import annotations
from pathlib import Path
import json
from datetime import datetime
from app.core.paths import project_outputs_root


def log_decision(project_id: str, kind: str, payload: dict) -> None:
    """kind: 'parse'|'map'|'price'|'subs'"""
    out_dir = project_outputs_root(project_id)
    path = out_dir / "audit.log.jsonl"
    rec = {"ts": datetime.utcnow().isoformat() + "Z", "kind": kind, **payload}

    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
