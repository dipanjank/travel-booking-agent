from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Auth
    jwt_secret: str
    jwt_access_token_expire_minutes: int = 30
    jwt_refresh_token_expire_days: int = 7
    admin_username: str = "admin"
    admin_email: str = "admin@example.com"
    admin_password: str

    # Database
    database_url: str

    # Agent
    mcp_server_url: str
    agent_model: str = "qwen.qwen3-next-80b-a3b"
    aws_region: str = "eu-west-1"

    model_config = {"env_prefix": "", "case_sensitive": False}


settings = Settings()
