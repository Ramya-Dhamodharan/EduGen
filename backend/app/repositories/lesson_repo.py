import uuid
from typing import List, Optional
from sqlalchemy.orm import Session

from app.models.lesson import Lesson
from app.models.module import Module
from app.schemas.lesson_schemas import LessonCreate, LessonUpdate


class LessonRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> List[Lesson]:
        return self.db.query(Lesson).all()

    def get_by_id(self, lesson_id: uuid.UUID) -> Optional[Lesson]:
        return self.db.query(Lesson).filter(Lesson.id == lesson_id).first()

    def module_exists(self, module_id: uuid.UUID) -> bool:
        return self.db.query(Module).filter(Module.id == module_id).first() is not None

    def create(self, data: LessonCreate) -> Lesson:
        lesson = Lesson(**data.model_dump())
        self.db.add(lesson)
        self.db.commit()
        self.db.refresh(lesson)
        return lesson

    def create_under_module(
        self, module_id: uuid.UUID, title: str, description: Optional[str], video_url: Optional[str]
    ) -> Lesson:
        lesson = Lesson(title=title, description=description, video_url=video_url, module_id=module_id)
        self.db.add(lesson)
        self.db.commit()
        self.db.refresh(lesson)
        return lesson

    def update(self, lesson: Lesson, data: LessonUpdate) -> Lesson:
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(lesson, field, value)
        self.db.commit()
        self.db.refresh(lesson)
        return lesson

    def delete(self, lesson: Lesson) -> None:
        self.db.delete(lesson)
        self.db.commit()