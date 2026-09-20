from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, Response

from backend.agent import create_agent
from backend.auth import authenticate, get_current_user
from backend.mcp_client import create_mcp_client
from backend.schemas import ChatRequest, ChatResponse, LoginRequest


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Start the MCP client, build the agent, and tear down on shutdown."""
    mcp_client = create_mcp_client()
    async with mcp_client:
        tools = mcp_client.get_tools()
        app.state.agent = create_agent(tools)
        yield


app = FastAPI(title="Travel Booking QA App", lifespan=lifespan)


@app.post("/login")
def login(request: LoginRequest, response: Response):
    """Authenticate and set a session cookie."""
    token = authenticate(request.username, request.password)
    response.set_cookie(key="session_token", value=token, httponly=True)
    return {"message": "Logged in"}


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, user: str = Depends(get_current_user)):
    """Send a message to the agent and return its reply."""
    agent = app.state.agent
    result = await agent.ainvoke(
        {"messages": [{"role": "user", "content": request.message}]},
        {"configurable": {"thread_id": request.session_id}},
    )
    reply = result["messages"][-1].content
    return ChatResponse(reply=reply, session_id=request.session_id)
