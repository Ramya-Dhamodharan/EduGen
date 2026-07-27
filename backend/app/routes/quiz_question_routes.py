import uuid
from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.user import User
from app.core.dependencies import get_current_user, require_staff, require_user
from app.schemas.quiz_question_schemas import (
    QuizQuestionCreate,
    QuizQuestionUpdate,
    QuizQuestionOut,
    QuizQuestionWithAnswerOut,
)
from app.services.quiz_question_service import QuizQuestionService

# Reads (without the correct answer) open to any logged-in user;
# writes are staff-only per-endpoint.
router = APIRouter(dependencies=[Depends(require_user)])


@router.get("", response_model=List[QuizQuestionOut])
def list_quiz_questions(db: Session = Depends(get_db)):
    return QuizQuestionService(db).list_all()


@router.get("/{question_id}", response_model=QuizQuestionOut)
def get_quiz_question(question_id: uuid.UUID, db: Session = Depends(get_db)):
    return QuizQuestionService(db).get(question_id)


@router.post("", response_model=QuizQuestionWithAnswerOut, status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(require_staff)])
def create_quiz_question(payload: QuizQuestionCreate, db: Session = Depends(get_db),
                         current_user: User = Depends(get_current_user)):
    return QuizQuestionService(db).create(payload, current_user.id)


@router.put("/{question_id}", response_model=QuizQuestionWithAnswerOut,
            dependencies=[Depends(require_staff)])
def update_quiz_question(question_id: uuid.UUID, payload: QuizQuestionUpdate, db: Session = Depends(get_db)):
    return QuizQuestionService(db).update(question_id, payload)


@router.delete("/{question_id}", status_code=status.HTTP_204_NO_CONTENT,
               dependencies=[Depends(require_staff)])
def delete_quiz_question(question_id: uuid.UUID, db: Session = Depends(get_db)):
    QuizQuestionService(db).delete(question_id)