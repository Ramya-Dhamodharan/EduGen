import uuid
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.security import hash_password
from app.models.user import User
from app.schemas.user_schemas import UserCreate, UserUpdate


class UserRepository:
    """Pure data-access layer for the users table."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(self) -> List[User]:
        result = await self.db.execute(select(User).options(selectinload(User.role)))
        return result.scalars().all()

    async def get_by_id(
        self,
        user_id: uuid.UUID,
    ) -> Optional[User]:
        result = await self.db.execute(
            select(User).options(selectinload(User.role)).where(User.id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_by_email(
        self,
        email: str,
    ) -> Optional[User]:
        result = await self.db.execute(
            select(User).options(selectinload(User.role)).where(User.email == email)
        )
        return result.scalar_one_or_none()

    async def create(
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
        await self.db.commit()

        return await self.get_by_id(user.id)

    async def update(
        self,
        user: User,
        data: UserUpdate,
    ) -> User:
        update_data = data.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(user, field, value)

        await self.db.commit()

        return await self.get_by_id(user.id)

    async def delete(
        self,
        user: User,
    ) -> None:
        await self.db.delete(user)
        await self.db.commit()
