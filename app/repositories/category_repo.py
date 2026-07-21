import uuid
from typing import List, Optional
from sqlalchemy.orm import Session

from app.models.category import Category
from app.models.course import Course
from app.schemas.category_schemas import CategoryCreate, CategoryUpdate


class CategoryRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> List[Category]:
        return self.db.query(Category).all()

    def get_by_id(self, category_id: uuid.UUID) -> Optional[Category]:
        return self.db.query(Category).filter(Category.id == category_id).first()

    def get_by_name(self, name: str) -> Optional[Category]:
        return self.db.query(Category).filter(Category.name == name).first()

    def create(self, data: CategoryCreate) -> Category:
        category = Category(name=data.name)
        self.db.add(category)
        self.db.commit()
        self.db.refresh(category)
        return category

    def update(self, category: Category, data: CategoryUpdate) -> Category:
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(category, field, value)
        self.db.commit()
        self.db.refresh(category)
        return category

    def delete(self, category: Category) -> None:
        self.db.delete(category)
        self.db.commit()

    def get_courses(self, category_id: uuid.UUID) -> List[Course]:
        return self.db.query(Course).filter(Course.category_id == category_id).all()