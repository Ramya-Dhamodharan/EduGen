import uuid
from typing import List

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.category import Category
from app.models.course import Course
from app.repositories.category_repo import CategoryRepository
from app.schemas.category_schemas import CategoryCreate, CategoryUpdate


class CategoryService:
    def __init__(self, db: AsyncSession):
        self.repo = CategoryRepository(db)

    async def list_categories(self) -> List[Category]:
        return await self.repo.get_all()

    async def get_category(self, category_id: uuid.UUID) -> Category:
        category = await self.repo.get_by_id(category_id)

        if not category:
            raise HTTPException(
                status.HTTP_404_NOT_FOUND,
                f"Category {category_id} not found",
            )

        return category

    async def create_category(
        self,
        data: CategoryCreate,
    ) -> Category:
        if await self.repo.get_by_name(data.name):
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                f"Category '{data.name}' already exists",
            )

        return await self.repo.create(data)

    async def update_category(
        self,
        category_id: uuid.UUID,
        data: CategoryUpdate,
    ) -> Category:
        category = await self.get_category(category_id)

        return await self.repo.update(
            category,
            data,
        )

    async def delete_category(
        self,
        category_id: uuid.UUID,
    ) -> None:
        category = await self.get_category(category_id)

        await self.repo.delete(category)

    async def get_courses_in_category(
        self,
        category_id: uuid.UUID,
    ) -> List[Course]:
        await self.get_category(category_id)

        return await self.repo.get_courses(category_id)