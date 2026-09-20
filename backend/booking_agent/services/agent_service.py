"""AgentService — manages the MCP client and LangGraph ReAct agent lifecycle."""

import logging

from langchain_aws import ChatBedrockConverse
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from langgraph.prebuilt import create_react_agent

from booking_agent.config import settings

logger = logging.getLogger(__name__)


class AgentService:
    """Singleton service that holds the MCP client and conversational agent.

    Created at application startup, torn down at shutdown.
    """

    def __init__(self) -> None:
        self._mcp_client: MultiServerMCPClient | None = None
        self._agent = None

    async def start(self) -> None:
        """Connect to the MCP server and build the ReAct agent."""
        self._mcp_client = MultiServerMCPClient(
            {
                "travel": {
                    "transport": "streamable_http",
                    "url": settings.mcp_server_url,
                },
            }
        )
        tools = await self._mcp_client.get_tools()
        logger.info("Loaded %d MCP tools", len(tools))

        model = ChatBedrockConverse(
            model=settings.agent_model,
            region_name=settings.aws_region,
        )

        checkpointer = AsyncPostgresSaver.from_conn_string(settings.database_url)
        await checkpointer.setup()

        self._agent = create_react_agent(model=model, tools=tools, checkpointer=checkpointer)
        logger.info("Agent service started")

    async def invoke(self, message: str, session_id: str) -> str:
        """Send a user message to the agent and return the assistant's reply."""
        result = await self._agent.ainvoke(
            {"messages": [{"role": "user", "content": message}]},
            {"configurable": {"thread_id": session_id}},
        )
        return result["messages"][-1].content

    async def stop(self) -> None:
        """Shut down the MCP client connection."""
        self._mcp_client = None
        self._agent = None
        logger.info("Agent service stopped")
