<<<<<<< HEAD
import uuid

from sqlalchemy.orm import Session

from app.models.quiz_attempt import QuizAttempt
from app.models.quiz_answer import QuizAnswer


class QuizAttemptRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, attempt_id: uuid.UUID) -> QuizAttempt | None:
        return (
            self.db.query(QuizAttempt)
            .filter(QuizAttempt.id == attempt_id)
            .first()
        )

    def get_all(self) -> list[QuizAttempt]:
        return self.db.query(QuizAttempt).all()

    def get_by_student_id(
        self,
        student_id: uuid.UUID,
    ) -> list[QuizAttempt]:
        return (
            self.db.query(QuizAttempt)
            .filter(QuizAttempt.student_id == student_id)
            .all()
        )

    def get_answers(
        self,
        attempt_id: uuid.UUID,
    ) -> list[QuizAnswer]:
        return (
            self.db.query(QuizAnswer)
            .filter(QuizAnswer.attempt_id == attempt_id)
            .all()
        )

    def create(self, attempt: QuizAttempt) -> QuizAttempt:
        self.db.add(attempt)
        self.db.commit()
        self.db.refresh(attempt)
        return attempt

    def update(self, attempt: QuizAttempt) -> QuizAttempt:
        self.db.commit()
        self.db.refresh(attempt)
        return attempt

    def delete(self, attempt: QuizAttempt) -> None:
        self.db.delete(attempt)
        self.db.commit()
=======
from datetime import datetime
from uuid import UUID

from fastapi import (
    HTTPException,
    status,
)

from sqlalchemy.orm import Session

from app.models.quiz import Quiz

from app.models.user import User

from app.models.quiz_attempt import QuizAttempt

from app.schemas.quiz_attempt import (
    QuizAttemptCreate,
    QuizAttemptUpdate,
    QuizAttemptSubmit,
)


# ==================================================
# START NEW QUIZ ATTEMPT
# ==================================================

def start_quiz_attempt(
    db: Session,
    attempt_data: QuizAttemptCreate,
):

    # -----------------------------------------
    # Check Student
    # -----------------------------------------

    student = db.query(User).filter(
        User.id == attempt_data.student_id
    ).first()

    if not student:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found",
        )

    # -----------------------------------------
    # Check Quiz
    # -----------------------------------------

    quiz = db.query(Quiz).filter(
        Quiz.id == attempt_data.quiz_id
    ).first()

    if not quiz:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quiz not found",
        )

    # -----------------------------------------
    # Find Previous Attempts
    # -----------------------------------------

    previous_attempts = db.query(
        QuizAttempt
    ).filter(
        QuizAttempt.student_id
        == attempt_data.student_id,

        QuizAttempt.quiz_id
        == attempt_data.quiz_id,
    ).count()

    # -----------------------------------------
    # Create Attempt
    # -----------------------------------------

    quiz_attempt = QuizAttempt(

        student_id=attempt_data.student_id,

        quiz_id=attempt_data.quiz_id,

        attempt_number=previous_attempts + 1,

        status="in_progress",
    )

    db.add(quiz_attempt)

    db.commit()

    db.refresh(quiz_attempt)

    return quiz_attempt


# ==================================================
# GET QUIZ ATTEMPT BY ID
# ==================================================

def get_quiz_attempt_by_id(
    db: Session,
    attempt_id: UUID,
):

    attempt = db.query(
        QuizAttempt
    ).filter(
        QuizAttempt.id == attempt_id
    ).first()

    if not attempt:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quiz attempt not found",
        )

    return attempt


# ==================================================
# UPDATE QUIZ ATTEMPT
# ==================================================

def update_quiz_attempt(
    db: Session,
    attempt_id: UUID,
    attempt_data: QuizAttemptUpdate,
):

    attempt = get_quiz_attempt_by_id(
        db,
        attempt_id,
    )

    update_data = attempt_data.model_dump(
        exclude_unset=True,
    )

    for field, value in update_data.items():

        setattr(
            attempt,
            field,
            value,
        )

    db.commit()

    db.refresh(attempt)

    return attempt


# ==================================================
# SUBMIT QUIZ ATTEMPT
# ==================================================

def submit_quiz_attempt(
    db: Session,
    attempt_id: UUID,
    submit_data: QuizAttemptSubmit,
):

    attempt = get_quiz_attempt_by_id(
        db,
        attempt_id,
    )

    # -----------------------------------------
    # Check Already Submitted
    # -----------------------------------------

    if attempt.status == "submitted":

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Quiz attempt is already submitted",
        )

    # -----------------------------------------
    # Update Attempt
    # -----------------------------------------

    attempt.score = submit_data.score

    attempt.status = "submitted"

    attempt.submitted_at = datetime.utcnow()

    db.commit()

    db.refresh(attempt)

    return attempt


# ==================================================
# DELETE QUIZ ATTEMPT
# ==================================================

def delete_quiz_attempt(
    db: Session,
    attempt_id: UUID,
):

    attempt = get_quiz_attempt_by_id(
        db,
        attempt_id,
    )

    db.delete(attempt)

    db.commit()

    return {
        "message": "Quiz attempt deleted successfully",
        "attempt_id": str(attempt_id),
    }


# ==================================================
# GET ATTEMPTS FOR STUDENT
# ==================================================

def get_student_quiz_attempts(
    db: Session,
    student_id: UUID,
):

    student = db.query(User).filter(
        User.id == student_id
    ).first()

    if not student:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found",
        )

    return (
        db.query(QuizAttempt)
        .filter(
            QuizAttempt.student_id
            == student_id
        )
        .order_by(
            QuizAttempt.started_at.desc()
        )
        .all()
    )


# ==================================================
# GET ATTEMPTS FOR QUIZ
# ==================================================

def get_quiz_attempts(
    db: Session,
    quiz_id: UUID,
):

    quiz = db.query(Quiz).filter(
        Quiz.id == quiz_id
    ).first()

    if not quiz:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quiz not found",
        )

    return (
        db.query(QuizAttempt)
        .filter(
            QuizAttempt.quiz_id
            == quiz_id
        )
        .order_by(
            QuizAttempt.started_at.desc()
        )
        .all()
    )
>>>>>>> origin/dev
