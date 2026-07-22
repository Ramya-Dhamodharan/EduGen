import uuid
from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.core.dependencies import require_staff, require_user
from app.schemas.module_schemas import ModuleCreate, ModuleUpdate, ModuleOut
from app.schemas.lesson_schemas import LessonCreate, LessonOut
from app.services.module_service import ModuleService
from app.services.lesson_service import LessonService

# Reads open to any logged-in user; writes restricted to staff below.
router = APIRouter(dependencies=[Depends(require_user)])


@router.get("", response_model=List[ModuleOut])
def list_modules(db: Session = Depends(get_db)):
    return ModuleService(db).list_modules()


@router.get("/{module_id}", response_model=ModuleOut)
def get_module(module_id: uuid.UUID, db: Session = Depends(get_db)):
    return ModuleService(db).get_module(module_id)


@router.post("", response_model=ModuleOut, status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(require_staff)])
def create_module(payload: ModuleCreate, db: Session = Depends(get_db)):
    return ModuleService(db).create_module(payload)


@router.put("/{module_id}", response_model=ModuleOut,
            dependencies=[Depends(require_staff)])
def update_module(module_id: uuid.UUID, payload: ModuleUpdate, db: Session = Depends(get_db)):
    return ModuleService(db).update_module(module_id, payload)


@router.delete("/{module_id}", status_code=status.HTTP_204_NO_CONTENT,
               dependencies=[Depends(require_staff)])
def delete_module(module_id: uuid.UUID, db: Session = Depends(get_db)):
    ModuleService(db).delete_module(module_id)


@router.get("/{module_id}/lessons", response_model=List[LessonOut])
def list_lessons_in_module(module_id: uuid.UUID, db: Session = Depends(get_db)):
    return ModuleService(db).get_lessons(module_id)


@router.post("/{module_id}/lessons", response_model=LessonOut, status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(require_staff)])
def create_lesson_under_module(module_id: uuid.UUID, payload: LessonCreate, db: Session = Depends(get_db)):
    return LessonService(db).create_lesson_under_module(module_id, payload.title, payload.description, payload.video_url)