from typing import Any, Generic, TypeVar

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from booking_agent.database import Base

T = TypeVar("T", bound=Base)


class GenericRepository(Generic[T]):
    """Base repository providing common CRUD operations."""

    def __init__(self, model: type[T], session: Session) -> None:
        self.model = model
        self.session = session

    def get_by_id(self, entity_id: Any) -> T | None:
        """Fetch an entity by its primary key."""
        return self.session.get(self.model, entity_id)

    def get_one(self, **filters: Any) -> T | None:
        """Fetch a single entity matching the given filters."""
        stmt = select(self.model).filter_by(**filters)
        return self.session.execute(stmt).scalar_one_or_none()

    def get_all(self, order_by: str | None = None) -> list[T]:
        """Fetch all entities, optionally ordered by a column name."""
        stmt = select(self.model)
        if order_by is not None:
            stmt = stmt.order_by(getattr(self.model, order_by))
        return list(self.session.execute(stmt).scalars().all())

    def count(self) -> int:
        """Return the total number of entities."""
        result = self.session.execute(select(func.count(self.model.id)))
        return result.scalar()

    def create(self, entity: T) -> T:
        """Insert an entity and commit."""
        self.session.add(entity)
        self.session.commit()
        self.session.refresh(entity)
        return entity

    def delete(self, entity: T) -> None:
        """Delete an entity and commit."""
        self.session.delete(entity)
        self.session.commit()
