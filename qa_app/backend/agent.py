import os

from langchain_core.tools import BaseTool
from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.prebuilt import create_react_agent

CHECKPOINT_POSTGRES_URL = os.environ.get("CHECKPOINT_POSTGRES_URL", "")
AGENT_MODEL = os.environ.get("AGENT_MODEL", "anthropic:claude-sonnet-4-20250514")


def create_agent(tools: list[BaseTool]) -> object:
    """Create a LangGraph ReAct agent backed by MCP tools.

    Uses PostgresSaver for conversation checkpointing when CHECKPOINT_POSTGRES_URL is set,
    otherwise runs without persistence.
    """
    checkpointer = PostgresSaver(conn_string=CHECKPOINT_POSTGRES_URL) if CHECKPOINT_POSTGRES_URL else None
    if checkpointer is not None:
        checkpointer.setup()

    return create_react_agent(
        model=AGENT_MODEL,
        tools=tools,
        checkpointer=checkpointer,
    )
