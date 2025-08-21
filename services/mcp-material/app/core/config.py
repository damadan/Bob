from pydantic_settings import BaseSettings
from pydantic import Field
from pathlib import Path


class Settings(BaseSettings):
    APP_NAME: str = "mcp-material"
    ENV: str = "dev"
    HOST: str = "0.0.0.0"
    PORT: int = 8080

    DATA_ROOT: Path = Field(default=Path("./data"))
    RESOURCES_ROOT: Path = Field(default=Path("./resources"))

    class Config:
        env_file = ".env"


settings = Settings()
