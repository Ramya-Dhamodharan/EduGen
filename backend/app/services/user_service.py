import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.certificate import Certificate
from app.models.enrollment import Enrollment
from app.models.payment import Payment
from app.models.user import User

from app.repositories.role_repo import RoleRepository
from app.repositories.user_repo import UserRepository

from app.schemas.user_schemas import (
    UserCreate,
    UserOut,
    UserUpdate,
)
from app.utils.exceptions import BadRequestError, NotFoundError


class UserService:
    """Business logic for user management."""

    def __init__(self, db: AsyncSession):
        self.repo = UserRepository(db)
        self.role_repo = RoleRepository(db)

    def _to_user_out(self, user: User) -> UserOut:
        return UserOut(
            id=user.id,
            username=user.username,
            email=user.email,
            role=user.role.name,
            is_active=user.is_active,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )

    async def list_users(self) -> list[UserOut]:
        users = await self.repo.get_all()
        return [self._to_user_out(user) for user in users]

    async def get_user(self, user_id: uuid.UUID) -> User:
        user = await self.repo.get_by_id(user_id)

        if user is None:
            raise NotFoundError(f"User with id '{user_id}' not found")

        return user

    async def get_user_out(self, user_id: uuid.UUID) -> UserOut:
        return self._to_user_out(await self.get_user(user_id))

    async def create_user(
        self,
        data: UserCreate,
    ) -> UserOut:

        if await self.repo.get_by_email(data.email):
            raise BadRequestError(f"Email '{data.email}' is already registered")

        if not await self.role_repo.get_by_id(data.role_id):
            raise BadRequestError(f"Role with id {data.role_id} does not exist")

        user = await self.repo.create(data)
        return self._to_user_out(user)

    async def update_user(
        self,
        user_id: uuid.UUID,
        data: UserUpdate,
    ) -> UserOut:

        user = await self.get_user(user_id)

        if data.role_id is not None and not await self.role_repo.get_by_id(
            data.role_id
        ):
            raise BadRequestError(f"Role with id {data.role_id} does not exist")

        user = await self.repo.update(user, data)
        return self._to_user_out(user)

    async def set_status(
        self,
        user_id: uuid.UUID,
        is_active: bool,
    ) -> UserOut:

        user = await self.get_user(user_id)

        user.is_active = is_active
        await self.repo.db.commit()
        await self.repo.db.refresh(user)
        return self._to_user_out(user)

    async def assign_role(
        self,
        user_id: uuid.UUID,
        role_id: int,
    ) -> UserOut:

        user = await self.get_user(user_id)

        if not await self.role_repo.get_by_id(role_id):
            raise BadRequestError(f"Role with id {role_id} does not exist")

        user.role_id = role_id

        await self.repo.db.commit()
        await self.repo.db.refresh(user)

        user = await self.repo.get_by_id(user.id)

        return self._to_user_out(user)

    async def list_enrollments(
        self,
        user_id: uuid.UUID,
    ) -> list[Enrollment]:

        await self.get_user(user_id)

        result = await self.repo.db.execute(
            select(Enrollment).where(Enrollment.student_id == user_id)
        )

        return result.scalars().all()

    async def list_certificates(
        self,
        user_id: uuid.UUID,
    ) -> list[Certificate]:

        await self.get_user(user_id)

        result = await self.repo.db.execute(
            select(Certificate).where(Certificate.student_id == user_id)
        )

        return result.scalars().all()

    async def list_payments(
        self,
        user_id: uuid.UUID,
    ) -> list[Payment]:

        await self.get_user(user_id)

        result = await self.repo.db.execute(
            select(Payment).where(Payment.student_id == user_id)
        )

        return result.scalars().all()

    async def delete_user(
        self,
        user_id: uuid.UUID,
    ) -> None:

        user = await self.get_user(user_id)

        await self.repo.delete(user)
