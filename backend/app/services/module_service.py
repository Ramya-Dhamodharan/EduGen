import uuid
from typing import List, Optional

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.lesson import Lesson
from app.models.module import Module
from app.repositories.module_repo import ModuleRepository
from app.schemas.module_schemas import ModuleCreate, ModuleUpdate


class ModuleService:
    def __init__(self, db: AsyncSession):
        self.repo = ModuleRepository(db)

    async def list_modules(self) -> List[Module]:
        return await self.repo.get_all()

    async def get_module(self, module_id: uuid.UUID) -> Module:
        module = await self.repo.get_by_id(module_id)

        if not module:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Module {module_id} not found",
            )

        return module

    async def create_module(
        self,
        data: ModuleCreate,
    ) -> Module:
        if not await self.repo.course_exists(data.course_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Course {data.course_id} does not exist",
            )

        return await self.repo.create(data)

    async def create_module_under_course(
        self,
        course_id: uuid.UUID,
        title: str,
        description: Optional[str],
    ) -> Module:

        if not await self.repo.course_exists(course_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Course {course_id} not found",
            )

        return await self.repo.create_under_course(
            course_id,
            title,
            description,
        )

    async def update_module(
        self,
        module_id: uuid.UUID,
        data: ModuleUpdate,
    ) -> Module:

        module = await self.get_module(module_id)

        return await self.repo.update(
            module,
            data,
        )

    async def delete_module(
        self,
        module_id: uuid.UUID,
    ) -> None:

        module = await self.get_module(module_id)
        await self.repo.delete(module)

    async def get_lessons(
        self,
        module_id: uuid.UUID,
    ) -> List[Lesson]:

        await self.get_module(module_id)

        return await self.repo.get_lessons(module_id)