from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """Incoming chat message from the user."""

    message: str = Field(..., min_length=1)
    session_id: str


class ChatResponse(BaseModel):
    """Agent reply sent back to the user."""

    reply: str
    session_id: str


class LoginRequest(BaseModel):
    """Credentials for the login endpoint."""

    username: str = Field(..., min_length=1)
    password: str = Field(..., min_length=1)
