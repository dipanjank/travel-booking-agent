from sqlalchemy import select
from sqlalchemy.orm import Session

from booking_agent.models.user import User
from booking_agent.repositories.base import GenericRepository


class UserRepository(GenericRepository[User]):
    """Repository for User entities with domain-specific queries."""

    def __init__(self, session: Session) -> None:
        super().__init__(User, session)

    def get_by_username_or_email(self, username: str, email: str) -> User | None:
        """Find a user matching either the given username or email."""
        result = self.session.execute(
            select(User).where((User.username == username) | (User.email == email))
        )
        return result.scalar_one_or_none()
