<<<<<<< HEAD
from uuid import UUID

from fastapi import (
    HTTPException,
    status,
)

from sqlalchemy.orm import Session

from app.models.quiz import Quiz

from app.models.quiz_question import QuizQuestion

from app.schemas.quiz_question_schemas import (
    QuizQuestionCreate,
    QuizQuestionUpdate,
    QuizQuestionNestedCreate,
)


# ==================================================
# CREATE QUIZ QUESTION
# ==================================================

def create_quiz_question(
    db: Session,
    question_data: QuizQuestionCreate,
):

    quiz = db.query(Quiz).filter(
        Quiz.id == question_data.quiz_id
    ).first()

    if not quiz:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quiz not found",
        )

    quiz_question = QuizQuestion(

        quiz_id=question_data.quiz_id,

        question=question_data.question,

        option_a=question_data.option_a,

        option_b=question_data.option_b,

        option_c=question_data.option_c,

        option_d=question_data.option_d,

        correct_option=question_data.correct_option,

        marks=question_data.marks,
    )

    db.add(quiz_question)

    db.commit()

    db.refresh(quiz_question)

    return quiz_question


# ==================================================
# CREATE QUESTION UNDER QUIZ
# ==================================================

def create_question_under_quiz(
    db: Session,
    quiz_id: UUID,
    question_data: QuizQuestionNestedCreate,
):

    quiz = db.query(Quiz).filter(
        Quiz.id == quiz_id
    ).first()

    if not quiz:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quiz not found",
        )

    quiz_question = QuizQuestion(

        quiz_id=quiz_id,

        question=question_data.question,

        option_a=question_data.option_a,

        option_b=question_data.option_b,

        option_c=question_data.option_c,

        option_d=question_data.option_d,

        correct_option=question_data.correct_option,

        marks=question_data.marks,
    )

    db.add(quiz_question)

    db.commit()

    db.refresh(quiz_question)

    return quiz_question


# ==================================================
# GET ALL QUIZ QUESTIONS
# ==================================================

def get_all_quiz_questions(
    db: Session,
):

    return (
        db.query(QuizQuestion)
        .order_by(
            QuizQuestion.created_at.desc()
        )
        .all()
    )


# ==================================================
# GET QUIZ QUESTION BY ID
# ==================================================

def get_quiz_question_by_id(
    db: Session,
    question_id: UUID,
):

    quiz_question = db.query(
        QuizQuestion
    ).filter(
        QuizQuestion.id == question_id
    ).first()

    if not quiz_question:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quiz question not found",
        )

    return quiz_question


# ==================================================
# UPDATE QUIZ QUESTION
# ==================================================

def update_quiz_question(
    db: Session,
    question_id: UUID,
    question_data: QuizQuestionUpdate,
):

    quiz_question = get_quiz_question_by_id(
        db,
        question_id,
    )

    update_data = question_data.model_dump(
        exclude_unset=True,
    )

    for field, value in update_data.items():

        setattr(
            quiz_question,
            field,
            value,
        )

    db.commit()

    db.refresh(quiz_question)

    return quiz_question


# ==================================================
# DELETE QUIZ QUESTION
# ==================================================

def delete_quiz_question(
    db: Session,
    question_id: UUID,
):

    quiz_question = get_quiz_question_by_id(
        db,
        question_id,
    )

    db.delete(quiz_question)

    db.commit()

    return {
        "message": "Quiz question deleted successfully",
        "question_id": str(question_id),
    }


# ==================================================
# GET QUESTIONS BY QUIZ
# ==================================================

def get_questions_by_quiz(
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
        db.query(QuizQuestion)
        .filter(
            QuizQuestion.quiz_id == quiz_id
        )
        .order_by(
            QuizQuestion.created_at.asc()
        )
        .all()
    )
=======
import uuid

from sqlalchemy.orm import Session

from app.models.quiz_question import QuizQuestion


class QuizQuestionRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, question_id: uuid.UUID) -> QuizQuestion | None:
        return (
            self.db.query(QuizQuestion)
            .filter(QuizQuestion.id == question_id)
            .first()
        )

    def get_all(self) -> list[QuizQuestion]:
        return self.db.query(QuizQuestion).all()

    def create(self, question: QuizQuestion) -> QuizQuestion:
        self.db.add(question)
        self.db.commit()
        self.db.refresh(question)
        return question

    def update(self, question: QuizQuestion) -> QuizQuestion:
        self.db.commit()
        self.db.refresh(question)
        return question

    def delete(self, question: QuizQuestion) -> None:
        self.db.delete(question)
        self.db.commit()
>>>>>>> 4cc63f074f7848968be0acde5a8d625115aaebb6
