import uuid
from typing import List, Optional
from sqlalchemy.orm import Session

from app.models.module import Module
from app.models.course import Course
from app.models.lesson import Lesson
from app.schemas.module_schemas import ModuleCreate, ModuleUpdate


class ModuleRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> List[Module]:
        return self.db.query(Module).all()

    def get_by_id(self, module_id: uuid.UUID) -> Optional[Module]:
        return self.db.query(Module).filter(Module.id == module_id).first()

    def course_exists(self, course_id: uuid.UUID) -> bool:
        return self.db.query(Course).filter(Course.id == course_id).first() is not None

    def create(self, data: ModuleCreate) -> Module:
        module = Module(**data.model_dump())
        self.db.add(module)
        self.db.commit()
        self.db.refresh(module)
        return module

    def create_under_course(self, course_id: uuid.UUID, title: str, description: Optional[str]) -> Module:
        module = Module(title=title, description=description, course_id=course_id)
        self.db.add(module)
        self.db.commit()
        self.db.refresh(module)
        return module

    def update(self, module: Module, data: ModuleUpdate) -> Module:
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(module, field, value)
        self.db.commit()
        self.db.refresh(module)
        return module

    def delete(self, module: Module) -> None:
        self.db.delete(module)
        self.db.commit()

    def get_lessons(self, module_id: uuid.UUID) -> List[Lesson]:
        return self.db.query(Lesson).filter(Lesson.module_id == module_id).all()