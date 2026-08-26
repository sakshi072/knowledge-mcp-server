import logging
from fastmcp import FastMCP
from mcp_server.tools.search_docs import search_knowledge_base
from mcp_server.core.settings import settings
import uvicorn
from starlette.responses import JSONResponse

logger = logging.getLogger(__name__)

mcp = FastMCP("MCP server exposing the knowledge-base search tool")

mcp.tool(search_knowledge_base)

@mcp.custom_route("/health", methods=["GET"])
async def health(request):
    """Health check endpoint"""
    return JSONResponse({"status": "healthy"})

app = mcp.http_app()

def start():
    logger.info(f"Starting MCP server on port {settings.PORT} (no inbound auth yet)")
    uvicorn.run(app, host="0.0.0.0", port=settings.PORT, log_level="info")

if __name__ == "__main__":
    start()