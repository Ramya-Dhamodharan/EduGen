import uuid
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.course import Course
from app.models.lesson import Lesson
from app.models.module import Module
from app.schemas.module_schemas import ModuleCreate, ModuleUpdate


class ModuleRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(self) -> List[Module]:
        result = await self.db.execute(select(Module))
        return result.scalars().all()

    async def get_by_id(
        self,
        module_id: uuid.UUID,
    ) -> Optional[Module]:
        result = await self.db.execute(
            select(Module).where(Module.id == module_id)
        )
        return result.scalar_one_or_none()

    async def course_exists(
        self,
        course_id: uuid.UUID,
    ) -> bool:
        result = await self.db.execute(
            select(Course).where(Course.id == course_id)
        )
        return result.scalar_one_or_none() is not None

    async def create(
        self,
        data: ModuleCreate,
    ) -> Module:
        module = Module(**data.model_dump())

        self.db.add(module)
        await self.db.commit()
        await self.db.refresh(module)

        return module

    async def create_under_course(
        self,
        course_id: uuid.UUID,
        title: str,
        description: Optional[str],
    ) -> Module:
        module = Module(
            title=title,
            description=description,
            course_id=course_id,
        )

        self.db.add(module)
        await self.db.commit()
        await self.db.refresh(module)

        return module

    async def update(
        self,
        module: Module,
        data: ModuleUpdate,
    ) -> Module:
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(module, field, value)

        await self.db.commit()
        await self.db.refresh(module)

        return module

    async def delete(
        self,
        module: Module,
    ) -> None:
        await self.db.delete(module)
        await self.db.commit()

    async def get_lessons(
        self,
        module_id: uuid.UUID,
    ) -> List[Lesson]:
        result = await self.db.execute(
            select(Lesson).where(
                Lesson.module_id == module_id
            )
        )
        return result.scalars().all()