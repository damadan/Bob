from __future__ import annotations
from pathlib import Path
from .config import settings


def project_outputs_root(project_id: str) -> Path:
    """Return path to outputs directory for a given project."""
    return Path(settings.DATA_ROOT) / "projects" / project_id / "outputs"


def ensure_parent(path: Path) -> None:
    """Ensure that the parent directory of ``path`` exists."""
    path.parent.mkdir(parents=True, exist_ok=True)
