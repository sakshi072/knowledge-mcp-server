import httpx
from mcp_server.core.settings import settings
from mcp_server.middleware.auth import get_token
from typing import Annotated
from pydantic import Field
import logging

logger = logging.getLogger(__name__)

async def search_knowledge_base(
    query: Annotated[str, Field(description="The search query string", min_length=1)],
    domain_name: Annotated[
        str,
        Field(description="Domain to search within, e.g. 'langchain-docs' or 'mcp-docs'"),
    ],
    top_k: Annotated[int, Field(gt=0, le=10, description="Number of results to return")] = 3,
) -> str:
    """Semantic search across the knowledge base for a given domain.
    """
    token = await get_token()

    logger.info(f"Searching domain={domain_name}: {query[:50]!r}")

    async with httpx.AsyncClient(
        base_url=str(settings.RETRIEVAL_BASE_URL), timeout=settings.RETRIEVAL_TIMEOUT
    ) as client:
        resp = await client.post(
            "/search",
            json = {"query":query, "domain_name": domain_name, "top_k":top_k},
            headers={"Authorization": f"Bearer {token}"}
        )
        resp.raise_for_status()
        return resp.text