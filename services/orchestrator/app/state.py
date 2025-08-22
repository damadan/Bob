from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional

class PipelineState(BaseModel):
    project_id: str
    file_uri: str
    region: str = "EU-Central"

    parsed: Optional[Dict[str, Any]] = None
    bom: Optional[Dict[str, Any]] = None
    priced: Optional[Dict[str, Any]] = None
    subs: Optional[Dict[str, Any]] = None

    export_json_path: Optional[str] = None
    export_xlsx_path: Optional[str] = None
    report_pdf_path: Optional[str] = None

    errors: List[str] = Field(default_factory=list)
