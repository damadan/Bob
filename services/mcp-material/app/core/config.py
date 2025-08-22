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

    CATALOG_MODEL_NAME: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    CATALOG_TOPK: int = 10
    CATALOG_MIN_SCORE: float = 0.55
    CATALOG_INDEX_PATH: Path = Field(default=Path("./resources/catalog/materials.faiss"))
    CATALOG_EMB_PATH: Path = Field(default=Path("./resources/catalog/materials.emb.jsonl"))

    class Config:
        env_file = ".env"


settings = Settings()
