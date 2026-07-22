<<<<<<< HEAD
import uuid
from typing import List
=======
from uuid import UUID
from app.repositories.quiz_question_repo import get_questions_by_quiz
from app.schemas.quiz_question import QuizQuestionResponse
>>>>>>> origin/dev

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

<<<<<<< HEAD
from app.db.database import get_db
from app.models.user import User
from app.core.dependencies import get_current_user, require_staff, require_user
from app.schemas.quiz_schemas import QuizCreate, QuizNestedCreate, QuizUpdate, QuizOut
from app.schemas.quiz_question_schemas import QuizQuestionOut, QuizQuestionNestedCreate
from app.services.quiz_service import QuizService

# Reads open to any logged-in user; writes are staff-only per-endpoint.
router = APIRouter(dependencies=[Depends(require_user)])


@router.get("", response_model=List[QuizOut])
def list_quizzes(db: Session = Depends(get_db)):
    return QuizService(db).list_all()


@router.get("/{quiz_id}", response_model=QuizOut)
def get_quiz(quiz_id: uuid.UUID, db: Session = Depends(get_db)):
    return QuizService(db).get(quiz_id)


@router.get("/{quiz_id}/questions", response_model=List[QuizQuestionOut])
def list_quiz_questions(quiz_id: uuid.UUID, db: Session = Depends(get_db)):
    return QuizService(db).list_questions(quiz_id)


@router.post("", response_model=QuizOut, status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(require_staff)])
def create_quiz(payload: QuizCreate, db: Session = Depends(get_db),
                current_user: User = Depends(get_current_user)):
    return QuizService(db).create(payload, current_user.id)


@router.put("/{quiz_id}", response_model=QuizOut, dependencies=[Depends(require_staff)])
def update_quiz(quiz_id: uuid.UUID, payload: QuizUpdate, db: Session = Depends(get_db)):
    return QuizService(db).update(quiz_id, payload)


@router.delete("/{quiz_id}", status_code=status.HTTP_204_NO_CONTENT,
               dependencies=[Depends(require_staff)])
def delete_quiz(quiz_id: uuid.UUID, db: Session = Depends(get_db)):
    QuizService(db).delete(quiz_id)


# Nested: create a question under a quiz (staff only)
@router.post("/{quiz_id}/questions", status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(require_staff)])
def create_question_under_quiz(
    quiz_id: uuid.UUID,
    payload: QuizQuestionNestedCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    from app.services.quiz_question_service import QuizQuestionService
    q = QuizQuestionService(db).create_under_quiz(quiz_id, payload, current_user.id)
    return {"id": str(q.id), "quiz_id": str(q.quiz_id), "position": q.position,
            "question": q.question, "marks": q.marks}

=======
from app.database import get_db

from app.schemas.quiz import (
    QuizCreate,
    QuizUpdate,
    QuizResponse,
)

from app.repositories.quiz_question_repo import (
    create_quiz,
    get_all_quizzes,
    get_quiz_by_id,
    update_quiz,
    delete_quiz,
    get_quizzes_by_course,
    create_quiz_under_course,
    activate_quiz,
    deactivate_quiz,
)


# ==================================================
# Quiz Router
# ==================================================

router = APIRouter()


# ==================================================
# GET ALL QUIZZES
# GET /api/quizzes
# ==================================================

@router.get(
    "",
    response_model=list[QuizResponse],
)
def get_quizzes(
    db: Session = Depends(get_db),
):
    return get_all_quizzes(db)


# ==================================================
# GET QUIZ BY ID
# GET /api/quizzes/{quiz_id}
# ==================================================

@router.get(
    "/{quiz_id}",
    response_model=QuizResponse,
)
def get_quiz(
    quiz_id: UUID,
    db: Session = Depends(get_db),
):
    return get_quiz_by_id(
        db,
        quiz_id,
    )


# ==================================================
# CREATE QUIZ
# POST /api/quizzes
# ==================================================

@router.post(
    "",
    response_model=QuizResponse,
    status_code=status.HTTP_201_CREATED,
)
def create(
    quiz_data: QuizCreate,
    db: Session = Depends(get_db),
):
    return create_quiz(
        db,
        quiz_data,
    )


# ==================================================
# UPDATE QUIZ
# PUT /api/quizzes/{quiz_id}
# ==================================================

@router.put(
    "/{quiz_id}",
    response_model=QuizResponse,
)
def update(
    quiz_id: UUID,
    quiz_data: QuizUpdate,
    db: Session = Depends(get_db),
):
    return update_quiz(
        db,
        quiz_id,
        quiz_data,
    )


# ==================================================
# DELETE QUIZ
# DELETE /api/quizzes/{quiz_id}
# ==================================================

@router.delete(
    "/{quiz_id}",
)
def delete(
    quiz_id: UUID,
    db: Session = Depends(get_db),
):
    return delete_quiz(
        db,
        quiz_id,
    )


# ==================================================
# ACTIVATE QUIZ
# PATCH /api/quizzes/{quiz_id}/activate
# ==================================================

@router.patch(
    "/{quiz_id}/activate",
    response_model=QuizResponse,
)
def activate(
    quiz_id: UUID,
    db: Session = Depends(get_db),
):
    return activate_quiz(
        db,
        quiz_id,
    )


# ==================================================
# DEACTIVATE QUIZ
# PATCH /api/quizzes/{quiz_id}/deactivate
# ==================================================

@router.patch(
    "/{quiz_id}/deactivate",
    response_model=QuizResponse,
)
def deactivate(
    quiz_id: UUID,
    db: Session = Depends(get_db),
):
    return deactivate_quiz(
        db,
        quiz_id,
    )


# ==================================================
# GET QUIZZES BY COURSE
# GET /api/courses/{course_id}/quizzes
# ==================================================

course_quiz_router = APIRouter()


@course_quiz_router.get(
    "/{course_id}/quizzes",
    response_model=list[QuizResponse],
)
def get_course_quizzes(
    course_id: UUID,
    db: Session = Depends(get_db),
):
    return get_quizzes_by_course(
        db,
        course_id,
    )


# ==================================================
# CREATE QUIZ UNDER COURSE
# POST /api/courses/{course_id}/quizzes
# ==================================================

@course_quiz_router.post(
    "/{course_id}/quizzes",
    response_model=QuizResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_course_quiz(
    course_id: UUID,
    quiz_data: QuizCreate,
    db: Session = Depends(get_db),
):
    return create_quiz_under_course(
        db,
        course_id,
        quiz_data,
    )
>>>>>>> origin/dev
