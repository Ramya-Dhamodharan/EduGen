import uuid
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.lesson import Lesson
from app.models.module import Module
from app.schemas.lesson_schemas import LessonCreate, LessonUpdate


class LessonRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(self) -> List[Lesson]:
        result = await self.db.execute(select(Lesson))
        return result.scalars().all()

    async def get_by_id(
        self,
        lesson_id: uuid.UUID,
    ) -> Optional[Lesson]:
        result = await self.db.execute(
            select(Lesson).where(Lesson.id == lesson_id)
        )
        return result.scalar_one_or_none()

    async def module_exists(
        self,
        module_id: uuid.UUID,
    ) -> bool:
        result = await self.db.execute(
            select(Module).where(Module.id == module_id)
        )
        return result.scalar_one_or_none() is not None

    async def create(
        self,
        data: LessonCreate,
    ) -> Lesson:
        lesson = Lesson(**data.model_dump())

        self.db.add(lesson)
        await self.db.commit()
        await self.db.refresh(lesson)

        return lesson

    async def create_under_module(
        self,
        module_id: uuid.UUID,
        title: str,
        description: Optional[str],
        video_url: Optional[str],
    ) -> Lesson:
        lesson = Lesson(
            title=title,
            description=description,
            video_url=video_url,
            module_id=module_id,
        )

        self.db.add(lesson)
        await self.db.commit()
        await self.db.refresh(lesson)

        return lesson

    async def update(
        self,
        lesson: Lesson,
        data: LessonUpdate,
    ) -> Lesson:
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(lesson, field, value)

        await self.db.commit()
        await self.db.refresh(lesson)

        return lesson

    async def delete(
        self,
        lesson: Lesson,
    ) -> None:
        await self.db.delete(lesson)
        await self.db.commit()