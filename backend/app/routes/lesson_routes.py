import uuid
from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.core.dependencies import require_staff, require_user
from app.schemas.lesson_schemas import LessonCreate, LessonUpdate, LessonOut
from app.services.lesson_service import LessonService

# Reads open to any logged-in user; writes restricted to staff below.
router = APIRouter(dependencies=[Depends(require_user)])


@router.get("", response_model=List[LessonOut])
def list_lessons(db: Session = Depends(get_db)):
    return LessonService(db).list_lessons()


@router.get("/{lesson_id}", response_model=LessonOut)
def get_lesson(lesson_id: uuid.UUID, db: Session = Depends(get_db)):
    return LessonService(db).get_lesson(lesson_id)


@router.post("", response_model=LessonOut, status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(require_staff)])
def create_lesson(payload: LessonCreate, db: Session = Depends(get_db)):
    return LessonService(db).create_lesson(payload)


@router.put("/{lesson_id}", response_model=LessonOut,
            dependencies=[Depends(require_staff)])
def update_lesson(lesson_id: uuid.UUID, payload: LessonUpdate, db: Session = Depends(get_db)):
    return LessonService(db).update_lesson(lesson_id, payload)


@router.delete("/{lesson_id}", status_code=status.HTTP_204_NO_CONTENT,
               dependencies=[Depends(require_staff)])
def delete_lesson(lesson_id: uuid.UUID, db: Session = Depends(get_db)):
    LessonService(db).delete_lesson(lesson_id)