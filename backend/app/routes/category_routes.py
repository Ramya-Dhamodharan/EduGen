import uuid
from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.category_schemas import CategoryCreate, CategoryUpdate, CategoryOut
from app.schemas.course_schemas import CourseOut
from app.services.category_service import CategoryService

router = APIRouter()


@router.get("", response_model=List[CategoryOut])
def list_categories(db: Session = Depends(get_db)):
    return CategoryService(db).list_categories()


@router.get("/{category_id}", response_model=CategoryOut)
def get_category(category_id: uuid.UUID, db: Session = Depends(get_db)):
    return CategoryService(db).get_category(category_id)


@router.post("", response_model=CategoryOut, status_code=status.HTTP_201_CREATED)
def create_category(payload: CategoryCreate, db: Session = Depends(get_db)):
    return CategoryService(db).create_category(payload)


@router.put("/{category_id}", response_model=CategoryOut)
def update_category(category_id: uuid.UUID, payload: CategoryUpdate, db: Session = Depends(get_db)):
    return CategoryService(db).update_category(category_id, payload)


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(category_id: uuid.UUID, db: Session = Depends(get_db)):
    CategoryService(db).delete_category(category_id)


@router.get("/{category_id}/courses", response_model=List[CourseOut])
def list_courses_in_category(category_id: uuid.UUID, db: Session = Depends(get_db)):
    return CategoryService(db).get_courses_in_category(category_id)