from typing import List

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.role import Role
from app.repositories.role_repo import RoleRepository
from app.schemas.role_schemas import RoleCreate, RoleUpdate


class RoleService:
    """
    Business rules live here (e.g. duplicate-name checks).
    Routes call this layer; this layer calls the repository.
    """

    def __init__(self, db: AsyncSession):
        self.repo = RoleRepository(db)

    async def list_roles(self) -> List[Role]:
        return await self.repo.get_all()

    async def get_role(self, role_id: int) -> Role:
        role = await self.repo.get_by_id(role_id)

        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Role with id {role_id} not found",
            )

        return role

    async def create_role(self, data: RoleCreate) -> Role:
        if await self.repo.get_by_name(data.name):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Role '{data.name}' already exists",
            )

        return await self.repo.create(data)

    async def update_role(
        self,
        role_id: int,
        data: RoleUpdate,
    ) -> Role:

        role = await self.get_role(role_id)

        return await self.repo.update(
            role,
            data,
        )

    async def delete_role(
        self,
        role_id: int,
    ) -> None:

        role = await self.get_role(role_id)

        await self.repo.delete(role)