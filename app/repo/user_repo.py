import uuid
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.config.security import hash_password
from app.models.user import User
from app.schema.user_schemas import UserCreate, UserUpdate


class UserRepository:
    """Pure data-access layer for the users table."""

    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> List[User]:
        result = self.db.execute(
            select(User).options(selectinload(User.role))
        )
        return result.scalars().all()

    def get_by_id(
        self,
        user_id: uuid.UUID,
    ) -> Optional[User]:
        result = self.db.execute(
            select(User)
            .options(selectinload(User.role))
            .where(User.id == user_id)
        )
        return result.scalar_one_or_none()

    def get_by_email(
        self,
        email: str,
    ) -> Optional[User]:
        result = self.db.execute(
            select(User)
            .options(selectinload(User.role))
            .where(User.email == email)
        )
        return result.scalar_one_or_none()

    def create(
        self,
        data: UserCreate,
    ) -> User:
        user = User(
            username=data.username,
            email=data.email,
            password_hash=hash_password(data.password),
            role_id=data.role_id,
            is_active=True,
        )

        self.db.add(user)
        self.db.commit()

        return self.get_by_id(user.id)

    def update(
        self,
        user: User,
        data: UserUpdate,
    ) -> User:
        update_data = data.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(user, field, value)

        self.db.commit()

        return self.get_by_id(user.id)

    def delete(
        self,
        user: User,
    ) -> None:
        self.db.delete(user)
        self.db.commit()