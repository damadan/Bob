from pydantic_settings import BaseSettings
from pydantic import AnyUrl

class Settings(BaseSettings):
    MCP_BASE_URL: AnyUrl = "http://localhost:8080"
    MCP_API_KEY: str | None = None
    MCP_REGION: str = "EU-Central"
    REQUEST_TIMEOUT: float = 30.0
    RETRIES: int = 3

    LLM_PROVIDER: str = "openai"     # openai | local
    LLM_MODEL: str = "gpt-4o-mini"
    OPENAI_API_KEY: str | None = None
    LOCAL_LLM_BASE_URL: str | None = None  # OpenAI-compatible endpoint

    class Config:
        env_file = ".env"

settings = Settings()
