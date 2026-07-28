import uuid
from typing import List
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.category import Category
from app.models.course import Course
from app.repositories.category_repo import CategoryRepository
from app.schemas.category_schemas import CategoryCreate, CategoryUpdate


class CategoryService:
    def __init__(self, db: Session):
        self.repo = CategoryRepository(db)

    def list_categories(self) -> List[Category]:
        return self.repo.get_all()

    def get_category(self, category_id: uuid.UUID) -> Category:
        category = self.repo.get_by_id(category_id)
        if not category:
            raise HTTPException(status.HTTP_404_NOT_FOUND, f"Category {category_id} not found")
        return category

    def create_category(self, data: CategoryCreate) -> Category:
        if self.repo.get_by_name(data.name):
            raise HTTPException(status.HTTP_400_BAD_REQUEST, f"Category '{data.name}' already exists")
        return self.repo.create(data)

    def update_category(self, category_id: uuid.UUID, data: CategoryUpdate) -> Category:
        category = self.get_category(category_id)
        return self.repo.update(category, data)

    def delete_category(self, category_id: uuid.UUID) -> None:
        category = self.get_category(category_id)
        self.repo.delete(category)

    def get_courses_in_category(self, category_id: uuid.UUID) -> List[Course]:
        self.get_category(category_id)  # raises 404 if missing
        return self.repo.get_courses(category_id)