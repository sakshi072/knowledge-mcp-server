import httpx
from mcp_server.core.settings import settings
from mcp_server.middleware.auth import get_token
from typing import Annotated
from pydantic import Field
import logging
import asyncio

logger = logging.getLogger(__name__)

MAX_ATTEMPTS = 2

# NOTE: domain names/descriptions are hardcoded to THIS deployment's
# actual domains - if this MCP server is ever reused for a different
# knowledge base, this needs updating manually. The robust fix is
# dynamic domain discovery from rag-mcp-service at startup - not built yet.
async def search_knowledge_base(
    query: Annotated[str, Field(description="The search query string", min_length=1)],
    domain_name: Annotated[
        str,
        Field(description="Domain to search within. Available domains: 'langchain-docs' "
                        "(LangChain and LangGraph docs, including using MCP servers as tools, "
                        "frontend integrations like generative UI/CopilotKit, middleware, agent tooling).")
    ],
    top_k: Annotated[int, Field(gt=0, le=10, description="Number of results to return")] = 5,
) -> str:
    """Semantic search across the knowledge base for a given domain.
    """
    token = await get_token()

    logger.info(f"Searching domain={domain_name}: {query[:50]!r}")

    timeout = httpx.Timeout(settings.RETRIEVAL_TIMEOUT, connect=5.0)
    last_exc: Exception | None = None

    async with httpx.AsyncClient(
        base_url=str(settings.RETRIEVAL_BASE_URL), timeout=timeout
    ) as client:
        for attempt in range(1, MAX_ATTEMPTS+1):
            try:
                resp = await client.post(
                    "/search",
                    json = {"query":query, "domain_name": domain_name, "top_k":top_k},
                    headers={"Authorization": f"Bearer {token}"}
                )
                if resp.status_code >=500:
                    raise httpx.HTTPStatusError("Server error", request=resp.request, response=resp)
                resp.raise_for_status()
                return resp.text
            except (httpx.TimeoutException, httpx.ConnectError, httpx.HTTPStatusError) as e:
                last_exc = e
                if isinstance(e, httpx.HTTPStatusError) and e.response.status_code < 500:
                    break
                logger.warning(f"search attempt {attempt}/{MAX_ATTEMPTS} failed: {type(e).__name__}")
                if attempt < MAX_ATTEMPTS:
                    await asyncio.sleep(0.5*attempt)
                    
    logger.error(f"search failed after retries: {type(last_exc).__name__}")
    raise RuntimeError(f"Knowledge base search unavailable ({type(last_exc).__name__})")