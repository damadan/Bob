import httpx
from .config import settings

def mcp_client() -> httpx.Client:
    headers = {}
    if settings.MCP_API_KEY:
        headers["x-api-key"] = settings.MCP_API_KEY
    return httpx.Client(base_url=str(settings.MCP_BASE_URL),
                        headers=headers,
                        timeout=settings.REQUEST_TIMEOUT)
