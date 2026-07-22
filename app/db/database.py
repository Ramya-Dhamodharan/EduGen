from collections.abc import Generator

from sqlalchemy import create_engine  # type: ignore[import]
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker # type: ignore[import]

from app.core.config import settings


engine = create_engine(
    settings.DATABASE_URL,
    future=True,
    pool_pre_ping=True,
    echo=settings.DEBUG,
)


SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
    future=True,
)


class Base(DeclarativeBase):
    """
    Base class for all SQLAlchemy ORM models.
    """
    pass


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency that provides a database session
    for each request and ensures it is closed afterwards.
    """
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()