"""Chat router — conversational flight search via the LangGraph agent."""

from fastapi import APIRouter, Depends

from booking_agent.dependencies import get_agent_service, get_current_user
from booking_agent.models.user import User
from booking_agent.schemas.chat import ChatRequest, ChatResponse
from booking_agent.services.agent_service import AgentService

router = APIRouter(prefix="/api", tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
async def chat(
    body: ChatRequest,
    user: User = Depends(get_current_user),
    agent: AgentService = Depends(get_agent_service),
) -> ChatResponse:
    """Send a message to the flight search agent and return its reply."""
    scoped_thread_id = f"{user.id}:{body.thread_id}"
    response = await agent.invoke(body.message, scoped_thread_id)
    return ChatResponse(response=response, thread_id=body.thread_id)
