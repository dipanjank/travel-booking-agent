import hashlib
import hmac
import os
import secrets

from fastapi import Cookie, HTTPException, status

APP_USERNAME = os.environ.get("APP_USERNAME", "admin")
APP_PASSWORD = os.environ.get("APP_PASSWORD", "changeme")

# In-memory session store: token -> username
_sessions: dict[str, str] = {}


def authenticate(username: str, password: str) -> str:
    """Validate credentials and return a session token.

    Raises HTTPException 401 if credentials are invalid.
    """
    username_ok = hmac.compare_digest(username, APP_USERNAME)
    password_ok = hmac.compare_digest(password, APP_PASSWORD)
    if not (username_ok and password_ok):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    token = hashlib.sha256(secrets.token_bytes(32)).hexdigest()
    _sessions[token] = username
    return token


def get_current_user(session_token: str | None = Cookie(None)) -> str:
    """FastAPI dependency that validates the session cookie.

    Returns the username associated with the session.
    Raises HTTPException 401 if the session is missing or invalid.
    """
    if session_token is None or session_token not in _sessions:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    return _sessions[session_token]
