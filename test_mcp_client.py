import asyncio
from fastmcp import Client

SEVER_URL = "http://localhost:8002/mcp"

async def main():
    async with Client(SEVER_URL) as client:
        tools = await client.list_tools()
        print(f"Connected. Available tools: {[t.name for t in tools]}\n")

        result = await client.call_tool(
            "search_knowledge_base",
            {
                "query": "How do I create an agent with tools and a model?",
                "domain_name": "langchain-hybrid",
                "top_k": 3,
            }
        )

        print("Tool result:")
        print(result)

if __name__ == "__main__":
    asyncio.run(main())