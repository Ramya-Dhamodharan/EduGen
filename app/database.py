from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

# The engine manages the actual connection pool to PostgreSQL
engine = create_engine(settings.DATABASE_URL)

# Each request gets its own Session from this factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# All models (in app/models/*.py) will inherit from this Base
Base = declarative_base()


def get_db():
    """
    FastAPI dependency: yields a DB session per-request and
    guarantees it's closed afterwards, even on error.
    Usage in a route:
        def endpoint(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
