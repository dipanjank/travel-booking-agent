import logging
from contextlib import asynccontextmanager

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

from fastapi import FastAPI

from booking_agent.config import settings
from booking_agent.database import SessionLocal
from booking_agent.dependencies import set_agent_service
from booking_agent.models.user import User
from booking_agent.repositories.user_repository import UserRepository
from booking_agent.routers.admin import router as admin_router
from booking_agent.routers.auth import router as auth_router
from booking_agent.routers.chat import router as chat_router
from booking_agent.services.agent_service import AgentService
from booking_agent.utils.auth import hash_password

logger = logging.getLogger(__name__)


def _seed_admin() -> None:
    """Create the initial admin user if one does not already exist."""
    with SessionLocal() as session:
        repo = UserRepository(session)
        existing = repo.get_one(role="ADMIN_USER")
        if existing is not None:
            return
        repo.create(
            User(
                username=settings.admin_username,
                email=settings.admin_email,
                password_hash=hash_password(settings.admin_password),
                role="ADMIN_USER",
            )
        )
        logger.info("Admin user '%s' seeded", settings.admin_username)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Seed admin user and start the agent service on startup."""
    _seed_admin()

    agent = AgentService()
    await agent.start()
    set_agent_service(agent)

    yield

    await agent.stop()
    set_agent_service(None)


app = FastAPI(title="Travel Booking QA App", lifespan=lifespan)
app.include_router(auth_router)
app.include_router(admin_router)
app.include_router(chat_router)


@app.get("/health")
def health() -> dict:
    """Health check endpoint for ALB target group."""
    return {"status": "ok"}
