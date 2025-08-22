from pydantic_settings import BaseSettings
from pydantic import Field, AnyUrl

class Settings(BaseSettings):
    MCP_BASE_URL: AnyUrl = "http://localhost:8080"
    MCP_API_KEY: str | None = None
    MCP_REGION: str = "EU-Central"
    REQUEST_TIMEOUT: float = 30.0
    RETRIES: int = 3

    class Config:
        env_file = ".env"

settings = Settings()
