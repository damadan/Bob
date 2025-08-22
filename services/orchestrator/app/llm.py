from __future__ import annotations
from langchain.chat_models.base import BaseChatModel
from langchain_openai import ChatOpenAI
from .config import settings
import os

def build_llm() -> BaseChatModel:
    prov = (settings.LLM_PROVIDER or "openai").lower()
    if prov == "openai":
        key = settings.OPENAI_API_KEY or os.getenv("OPENAI_API_KEY")
        if not key:
            raise RuntimeError("OPENAI_API_KEY is not set. Export it or set in .env")
        return ChatOpenAI(model=settings.LLM_MODEL, temperature=0, api_key=key)
    elif prov == "local":
        base = settings.LOCAL_LLM_BASE_URL or "http://localhost:8000/v1"
        return ChatOpenAI(model=settings.LLM_MODEL, temperature=0, api_key="dummy", base_url=base)
    else:
        raise ValueError(f"Unknown LLM_PROVIDER={settings.LLM_PROVIDER}")
