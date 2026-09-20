from fastapi import APIRouter, Depends, Response

from booking_agent.config import settings
from booking_agent.dependencies import get_auth_service, get_current_user, get_refresh_token
from booking_agent.schemas.auth import LoginRequest, TokenResponse
from booking_agent.services.auth_service import AuthService

router = APIRouter(prefix="/api/auth", tags=["auth"])

REFRESH_COOKIE_MAX_AGE = settings.jwt_refresh_token_expire_days * 86400


def _set_refresh_cookie(response: Response, token: str) -> None:
    """Set the refresh token as an HttpOnly cookie on the response."""
    response.set_cookie(
        key="refresh_token",
        value=token,
        httponly=True,
        secure=False,  # Set True in production behind HTTPS
        samesite="strict",
        path="/api/auth",
        max_age=REFRESH_COOKIE_MAX_AGE,
    )


@router.post("/login", response_model=TokenResponse)
def login(
    body: LoginRequest,
    response: Response,
    service: AuthService = Depends(get_auth_service),
) -> TokenResponse:
    """Authenticate with username and password.

    Returns an access token in the response body and sets a refresh token
    as an HttpOnly cookie.
    """
    token_response, refresh_token = service.login(body)
    _set_refresh_cookie(response, refresh_token)
    return token_response


@router.post("/refresh", response_model=TokenResponse)
def refresh(
    response: Response,
    token: str = Depends(get_refresh_token),
    service: AuthService = Depends(get_auth_service),
) -> TokenResponse:
    """Issue a new access token using a valid refresh token cookie."""
    token_response, new_refresh_token = service.refresh(token)
    _set_refresh_cookie(response, new_refresh_token)
    return token_response


@router.post("/logout")
def logout(
    response: Response,
    _=Depends(get_current_user),
) -> dict:
    """Log out by deleting the refresh token cookie."""
    response.delete_cookie(key="refresh_token", path="/api/auth")
    return {"message": "Logged out"}
