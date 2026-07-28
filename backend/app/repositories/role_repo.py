from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.role import Role
from app.schemas.role_schemas import RoleCreate, RoleUpdate


class RoleRepository:
    """
    Pure data-access layer. No business rules here — just talks to the DB.
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(self) -> List[Role]:
        result = await self.db.execute(
            select(Role)
        )
        return result.scalars().all()

    async def get_by_id(
        self,
        role_id: int,
    ) -> Optional[Role]:
        result = await self.db.execute(
            select(Role).where(Role.id == role_id)
        )
        return result.scalar_one_or_none()

    async def get_by_name(
        self,
        name: str,
    ) -> Optional[Role]:
        # Case-insensitive so "student" also matches a "Student" row.
        result = await self.db.execute(
            select(Role).where(Role.name.ilike(name))
        )
        return result.scalar_one_or_none()

    async def create(
        self,
        data: RoleCreate,
    ) -> Role:
        role = Role(name=data.name)

        self.db.add(role)
        await self.db.commit()
        await self.db.refresh(role)

        return role

    async def update(
        self,
        role: Role,
        data: RoleUpdate,
    ) -> Role:
        update_data = data.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(role, field, value)

        await self.db.commit()
        await self.db.refresh(role)

        return role

    async def delete(
        self,
        role: Role,
    ) -> None:
        await self.db.delete(role)
        await self.db.commit()