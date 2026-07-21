import sys
import os
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# Make sure "app" package is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.core.config import settings
from EduGen.app.db.database import Base

# IMPORTANT: import every model here so Alembic "sees" the tables
# when autogenerating migrations. Add each new model file as you create it.
from app.models.role import Role
from app.models.user import User
from app.models.category import Category
from app.models.course import Course
from app.models.module import Module
from app.models.lesson import Lesson
from app.models.enrollment import Enrollment
from app.models.quiz import Quiz
from app.models.quiz_question import QuizQuestion
from app.models.quiz_attempt import QuizAttempt
from app.models.quiz_answer import QuizAnswer
from app.models.certificate import Certificate
from app.models.course_review import CourseReview
from app.models.payment import Payment

config = context.config

# Pull DB URL from our own settings/.env instead of alembic.ini
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# This tells Alembic what your models currently look like,
# so it can diff against the live DB and autogenerate migrations.
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
