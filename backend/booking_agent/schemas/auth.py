from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    """Credentials for the login endpoint."""

    username: str = Field(..., min_length=1)
    password: str = Field(..., min_length=1)


class TokenResponse(BaseModel):
    """JWT token response returned on successful login or refresh."""

    access_token: str
    token_type: str = "bearer"
    expires_in: int
