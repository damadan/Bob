from pathlib import Path
from fastapi import HTTPException
from .config import settings

class ResourceUriResolver:
    """
    Поддерживаемые схемы:
      resource://project/<id>/files/...   -> {DATA_ROOT}/projects/<id>/files/...
      resource://pricebook/<region>       -> {RESOURCES_ROOT}/pricebook/<region>/pricebook.jsonl
      resource://catalog/materials        -> {RESOURCES_ROOT}/catalog/materials.jsonl
    """
    def __init__(self, data_root: Path = settings.DATA_ROOT, res_root: Path = settings.RESOURCES_ROOT):
        self.data_root = Path(data_root)
        self.res_root = Path(res_root)

    def resolve(self, uri: str) -> Path:
        if not uri.startswith("resource://"):
            raise HTTPException(status_code=400, detail="Unsupported URI scheme")

        parts = uri.removeprefix("resource://").split("/")
        head = parts[0] if parts else None

        if head == "project":
            if len(parts) < 3 or parts[2] != "files":
                raise HTTPException(status_code=400, detail="Malformed project URI")
            project_id = parts[1]
            tail = parts[3:]
            path = self.data_root / "projects" / project_id / "files" / Path(*tail)
            return path.resolve()

        if head == "pricebook":
            if len(parts) != 2:
                raise HTTPException(status_code=400, detail="Malformed pricebook URI")
            region = parts[1]
            path = self.res_root / "pricebook" / region / "pricebook.jsonl"
            return path.resolve()

        if head == "catalog":
            if len(parts) != 2 or parts[1] != "materials":
                raise HTTPException(status_code=400, detail="Malformed catalog URI")
            path = self.res_root / "catalog" / "materials.jsonl"
            return path.resolve()

        raise HTTPException(status_code=400, detail=f"Unknown resource head: {head}")
