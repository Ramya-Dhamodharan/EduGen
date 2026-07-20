from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Central place for all environment-driven configuration.
    Values are loaded from the .env file at project root.
    """
    APP_NAME: str = "EduGen"
    DEBUG: bool = True

    DATABASE_URL: str

    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    class Config:
        env_file = ".env"


# Import this single instance anywhere you need config:
# from app.core.config import settings
settings = Settings()
