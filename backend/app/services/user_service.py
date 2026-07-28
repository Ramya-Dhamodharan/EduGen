import uuid
from typing import List

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.enrollment import Enrollment
from app.models.certificate import Certificate
from app.models.payment import Payment

from app.repositories.user_repo import UserRepository
from app.repositories.role_repo import RoleRepository

from app.schemas.user_schemas import UserCreate, UserUpdate


class UserService:
    """Business rules for users (uniqueness, role validation, etc.)."""

    def __init__(self, db: AsyncSession):
        self.repo = UserRepository(db)
        self.role_repo = RoleRepository(db)

    async def list_users(self) -> List[User]:
        return await self.repo.get_all()

    async def get_user(self, user_id: uuid.UUID) -> User:
        user = await self.repo.get_by_id(user_id)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with id {user_id} not found",
            )

        return user

    async def create_user(
        self,
        data: UserCreate,
    ) -> User:

        if await self.repo.get_by_email(data.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Email '{data.email}' is already registered",
            )

        if not await self.role_repo.get_by_id(data.role_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Role with id {data.role_id} does not exist",
            )

        return await self.repo.create(data)

    async def update_user(
        self,
        user_id: uuid.UUID,
        data: UserUpdate,
    ) -> User:

        user = await self.get_user(user_id)

        if (
            data.role_id is not None
            and not await self.role_repo.get_by_id(data.role_id)
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Role with id {data.role_id} does not exist",
            )

        return await self.repo.update(user, data)

    async def set_status(
        self,
        user_id: uuid.UUID,
        is_active: bool,
    ) -> User:

        user = await self.get_user(user_id)

        user.is_active = is_active

        await self.repo.db.commit()
        await self.repo.db.refresh(user)

        return user

    async def assign_role(
        self,
        user_id: uuid.UUID,
        role_id: int,
    ) -> User:

        user = await self.get_user(user_id)

        if not await self.role_repo.get_by_id(role_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Role with id {role_id} does not exist",
            )

        user.role_id = role_id

        await self.repo.db.commit()
        await self.repo.db.refresh(user)

        return user

    async def list_enrollments(
        self,
        user_id: uuid.UUID,
    ) -> List[Enrollment]:

        await self.get_user(user_id)

        result = await self.repo.db.execute(
            select(Enrollment).where(
                Enrollment.student_id == user_id
            )
        )

        return result.scalars().all()

    async def list_certificates(
        self,
        user_id: uuid.UUID,
    ) -> List[Certificate]:

        await self.get_user(user_id)

        result = await self.repo.db.execute(
            select(Certificate).where(
                Certificate.student_id == user_id
            )
        )

        return result.scalars().all()

    async def list_payments(
        self,
        user_id: uuid.UUID,
    ) -> List[Payment]:

        await self.get_user(user_id)

        result = await self.repo.db.execute(
            select(Payment).where(
                Payment.student_id == user_id
            )
        )

        return result.scalars().all()

    async def delete_user(
        self,
        user_id: uuid.UUID,
    ) -> None:

        user = await self.get_user(user_id)

        await self.repo.delete(user)