from pydantic import BaseModel


class Health(BaseModel):
    status: str = "ok"
    service: str = "mcp-material"
    version: str = "0.0.1"


class Error(BaseModel):
    detail: str
