import uuid
from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.module import Module
from app.models.lesson import Lesson
from app.repositories.module_repo import ModuleRepository
from app.schemas.module_schemas import ModuleCreate, ModuleUpdate


class ModuleService:
    def __init__(self, db: Session):
        self.repo = ModuleRepository(db)

    def list_modules(self) -> List[Module]:
        return self.repo.get_all()

    def get_module(self, module_id: uuid.UUID) -> Module:
        module = self.repo.get_by_id(module_id)
        if not module:
            raise HTTPException(status.HTTP_404_NOT_FOUND, f"Module {module_id} not found")
        return module

    def create_module(self, data: ModuleCreate) -> Module:
        if not self.repo.course_exists(data.course_id):
            raise HTTPException(status.HTTP_400_BAD_REQUEST, f"Course {data.course_id} does not exist")
        return self.repo.create(data)

    def create_module_under_course(self, course_id: uuid.UUID, title: str, description: Optional[str]) -> Module:
        if not self.repo.course_exists(course_id):
            raise HTTPException(status.HTTP_404_NOT_FOUND, f"Course {course_id} not found")
        return self.repo.create_under_course(course_id, title, description)

    def update_module(self, module_id: uuid.UUID, data: ModuleUpdate) -> Module:
        module = self.get_module(module_id)
        return self.repo.update(module, data)

    def delete_module(self, module_id: uuid.UUID) -> None:
        module = self.get_module(module_id)
        self.repo.delete(module)

    def get_lessons(self, module_id: uuid.UUID) -> List[Lesson]:
        self.get_module(module_id)
        return self.repo.get_lessons(module_id)