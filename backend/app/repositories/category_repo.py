import uuid
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.category import Category
from app.models.course import Course
from app.schemas.category_schemas import CategoryCreate, CategoryUpdate


class CategoryRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(self) -> List[Category]:
        result = await self.db.execute(select(Category))
        return result.scalars().all()

    async def get_by_id(self, category_id: uuid.UUID) -> Optional[Category]:
        result = await self.db.execute(
            select(Category).where(Category.id == category_id)
        )
        return result.scalar_one_or_none()

    async def get_by_name(self, name: str) -> Optional[Category]:
        result = await self.db.execute(select(Category).where(Category.name == name))
        return result.scalar_one_or_none()

    async def create(self, data: CategoryCreate) -> Category:
        category = Category(name=data.name)

        self.db.add(category)
        await self.db.commit()
        await self.db.refresh(category)

        return category

    async def update(
        self,
        category: Category,
        data: CategoryUpdate,
    ) -> Category:
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(category, field, value)

        await self.db.commit()
        await self.db.refresh(category)

        return category

    async def delete(self, category: Category) -> None:
        await self.db.delete(category)
        await self.db.commit()

    async def get_courses(self, category_id: uuid.UUID) -> List[Course]:
        result = await self.db.execute(
            select(Course).where(Course.category_id == category_id)
        )
        return result.scalars().all()
