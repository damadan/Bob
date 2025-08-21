from pathlib import Path
from typing import Optional
from .config import settings

def project_files_root(project_id: str) -> Path:
    base = settings.DATA_ROOT / "projects" / project_id / "files"
    base.mkdir(parents=True, exist_ok=True)
    return base

def project_outputs_root(project_id: str) -> Path:
    base = settings.DATA_ROOT / "projects" / project_id / "outputs"
    base.mkdir(parents=True, exist_ok=True)
    return base

def ensure_parent(path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    return path
