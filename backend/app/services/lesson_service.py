import uuid
from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.lesson import Lesson
from app.repositories.lesson_repo import LessonRepository
from app.schemas.lesson_schemas import LessonCreate, LessonUpdate


class LessonService:
    def __init__(self, db: Session):
        self.repo = LessonRepository(db)

    def list_lessons(self) -> List[Lesson]:
        return self.repo.get_all()

    def get_lesson(self, lesson_id: uuid.UUID) -> Lesson:
        lesson = self.repo.get_by_id(lesson_id)
        if not lesson:
            raise HTTPException(status.HTTP_404_NOT_FOUND, f"Lesson {lesson_id} not found")
        return lesson

    def create_lesson(self, data: LessonCreate) -> Lesson:
        if not self.repo.module_exists(data.module_id):
            raise HTTPException(status.HTTP_400_BAD_REQUEST, f"Module {data.module_id} does not exist")
        return self.repo.create(data)

    def create_lesson_under_module(
        self, module_id: uuid.UUID, title: str, description: Optional[str], video_url: Optional[str]
    ) -> Lesson:
        if not self.repo.module_exists(module_id):
            raise HTTPException(status.HTTP_404_NOT_FOUND, f"Module {module_id} not found")
        return self.repo.create_under_module(module_id, title, description, video_url)

    def update_lesson(self, lesson_id: uuid.UUID, data: LessonUpdate) -> Lesson:
        lesson = self.get_lesson(lesson_id)
        return self.repo.update(lesson, data)

    def delete_lesson(self, lesson_id: uuid.UUID) -> None:
        lesson = self.get_lesson(lesson_id)
        self.repo.delete(lesson)