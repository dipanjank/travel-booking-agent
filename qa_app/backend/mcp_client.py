import os

from langchain_mcp_adapters.client import MultiServerMCPClient

MCP_SERVER_URL = os.environ.get("MCP_SERVER_URL", "http://localhost:8001/mcp")


def create_mcp_client() -> MultiServerMCPClient:
    """Create a MultiServerMCPClient configured to connect to the travel MCP server."""
    return MultiServerMCPClient(
        {
            "travel": {
                "transport": "streamable_http",
                "url": MCP_SERVER_URL,
            },
        }
    )
