<<<<<<< HEAD
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.quiz_answer_schemas import (
    QuizAnswerCreate,
    QuizAnswerUpdate,
    QuizAnswerResponse
)
from app.services import quiz_answer_service
router = APIRouter(
    prefix="/api",
    tags=["Quiz Answers"]
)


@router.get(
    "/quiz-answers",
    response_model=list[QuizAnswerResponse],
    status_code=status.HTTP_200_OK
)
def get_all_quiz_answers(
    db: Session = Depends(get_db)
):
    return quiz_answer_service.get_all_answers(db)


@router.get(
    "/quiz-answers/{answer_id}",
    response_model=QuizAnswerResponse,
    status_code=status.HTTP_200_OK
)
def get_quiz_answer(
    answer_id: UUID,
    db: Session = Depends(get_db)
):
    return quiz_answer_service.get_answer_by_id(
        db,
        answer_id
    )


@router.post(
    "/quiz-answers",
    response_model=QuizAnswerResponse,
    status_code=status.HTTP_201_CREATED
)
def create_quiz_answer(
    answer: QuizAnswerCreate,
    db: Session = Depends(get_db)
):
    return quiz_answer_service.create_answer(
        db,
        answer
    )


@router.put(
    "/quiz-answers/{answer_id}",
    response_model=QuizAnswerResponse,
    status_code=status.HTTP_200_OK
)
def update_quiz_answer(
    answer_id: UUID,
    answer: QuizAnswerUpdate,
    db: Session = Depends(get_db)
):
    return quiz_answer_service.update_answer(
        db,
        answer_id,
        answer
    )


@router.delete(
    "/quiz-answers/{answer_id}",
    status_code=status.HTTP_200_OK
)
def delete_quiz_answer(
    answer_id: UUID,
    db: Session = Depends(get_db)
):
    return quiz_answer_service.delete_answer(
        db,
        answer_id
    )


@router.get(
    "/quiz-attempts/{attempt_id}/answers",
    response_model=list[QuizAnswerResponse],
    status_code=status.HTTP_200_OK
)
def get_answers_by_attempt(
    attempt_id: UUID,
    db: Session = Depends(get_db)
):
    return quiz_answer_service.get_answers_by_attempt(
        db,
        attempt_id
    )


@router.post(
    "/quiz-attempts/{attempt_id}/answers",
    response_model=QuizAnswerResponse,
    status_code=status.HTTP_201_CREATED
)
def submit_answer_under_attempt(
    attempt_id: UUID,
    answer: QuizAnswerCreate,
    db: Session = Depends(get_db)
):
    answer.attempt_id = attempt_id

    return quiz_answer_service.create_answer(
        db,
        answer
    )
=======
import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.user import User
from app.models.quiz_attempt import QuizAttempt
from app.core.dependencies import get_current_user, require_staff
from app.schemas.quiz_answer_schemas import (
    QuizAnswerCreate,
    QuizAnswerUpdate,
    QuizAnswerOut,
)
from app.services.quiz_answer_service import QuizAnswerService

router = APIRouter()


def _is_staff(user: User) -> bool:
    return user.role.name.lower() in ("admin", "instructor")


def _owner_of_answer(db: Session, attempt_id: uuid.UUID) -> uuid.UUID | None:
    attempt = db.query(QuizAttempt).filter(QuizAttempt.id == attempt_id).first()
    return attempt.student_id if attempt else None


# ---- Staff: list all answers ----
@router.get("", response_model=List[QuizAnswerOut], dependencies=[Depends(require_staff)])
def list_answers(db: Session = Depends(get_db)):
    return QuizAnswerService(db).list_all()


# ---- Owner or staff: view one ----
@router.get("/{answer_id}", response_model=QuizAnswerOut)
def get_answer(answer_id: uuid.UUID, db: Session = Depends(get_db),
               current_user: User = Depends(get_current_user)):
    answer = QuizAnswerService(db).get(answer_id)
    owner = _owner_of_answer(db, answer.attempt_id)
    if not _is_staff(current_user) and current_user.id != owner:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "You do not have permission to access this resource")
    return answer


# ---- Student submits their own answer ----
@router.post("", response_model=QuizAnswerOut, status_code=status.HTTP_201_CREATED)
def submit_answer(payload: QuizAnswerCreate, db: Session = Depends(get_db),
                  current_user: User = Depends(get_current_user)):
    owner = _owner_of_answer(db, payload.attempt_id)
    if owner is None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, f"Attempt {payload.attempt_id} does not exist")
    if not _is_staff(current_user) and current_user.id != owner:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "You can only submit answers for your own attempt")
    return QuizAnswerService(db).submit(payload.attempt_id, payload.question_id,
                                        payload.selected_option, current_user.id)


# ---- Owner or staff: update an answer ----
@router.put("/{answer_id}", response_model=QuizAnswerOut)
def update_answer(answer_id: uuid.UUID, payload: QuizAnswerUpdate, db: Session = Depends(get_db),
                  current_user: User = Depends(get_current_user)):
    answer = QuizAnswerService(db).get(answer_id)
    owner = _owner_of_answer(db, answer.attempt_id)
    if not _is_staff(current_user) and current_user.id != owner:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "You do not have permission to access this resource")
    return QuizAnswerService(db).update(answer_id, payload.selected_option)
>>>>>>> 4cc63f074f7848968be0acde5a8d625115aaebb6
