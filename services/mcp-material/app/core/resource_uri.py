from pathlib import Path
from urllib.parse import unquote
from fastapi import HTTPException
from .config import settings

class ResourceUriResolver:
    """
    Supported schemes:
      resource://project/<id>/files/...   -> {DATA_ROOT}/projects/<id>/files/...
      resource://pricebook/<region>       -> {RESOURCES_ROOT}/pricebook/<region>/pricebook.jsonl
      resource://catalog/materials        -> {RESOURCES_ROOT}/catalog/materials.jsonl
    """

    def __init__(self, data_root: Path = settings.DATA_ROOT, res_root: Path = settings.RESOURCES_ROOT):
        self.data_root = Path(data_root)
        self.res_root = Path(res_root)

    def _ensure_under(self, path: Path, root: Path) -> Path:
        resolved = path.resolve()
        try:
            resolved.relative_to(root.resolve())
        except ValueError:
            raise HTTPException(status_code=400, detail="Path escapes allowed root")
        return resolved

    def resolve(self, uri: str) -> Path:
        if not uri.startswith("resource://"):
            raise HTTPException(status_code=400, detail="Unsupported URI scheme")

        raw = uri.removeprefix("resource://")
        decoded = unquote(raw)

        # Block traversal and hidden encodings
        if ".." in decoded or "%2e" in raw.lower():
            raise HTTPException(status_code=400, detail="Parent segments are not allowed")

        parts = decoded.split("/")
        head = parts[0] if parts else None

        if head == "project":
            if len(parts) < 3 or parts[2] != "files":
                raise HTTPException(status_code=400, detail="Malformed project URI")
            project_id = parts[1]
            tail = parts[3:]
            base = self.data_root / "projects" / project_id / "files"
            path = base / Path(*tail)
            return self._ensure_under(path, base)

        if head == "pricebook":
            if len(parts) != 2:
                raise HTTPException(status_code=400, detail="Malformed pricebook URI")
            region = parts[1]
            base = self.res_root / "pricebook" / region
            path = base / "pricebook.jsonl"
            return self._ensure_under(path, base)

        if head == "catalog":
            if len(parts) != 2 or parts[1] != "materials":
                raise HTTPException(status_code=400, detail="Malformed catalog URI")
            base = self.res_root / "catalog"
            path = base / "materials.jsonl"
            return self._ensure_under(path, base)

        raise HTTPException(status_code=400, detail=f"Unknown resource head: {head}")
