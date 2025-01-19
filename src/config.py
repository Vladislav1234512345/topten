import logging

from pydantic_settings import BaseSettings, SettingsConfigDict
from src.container import BASE_DIR


class WebSettings(BaseSettings):
    WEBAPP_HOST: str
    WEBAPP_PORT: int
    FRONTEND_LINK: str
    CORS_ALLOWED_ORIGINS: str

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / "env_files/.env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )


class DatabaseSettings(BaseSettings):
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int
    POSTGRES_DB: str

    @property
    def POSTGRES_URL_psycopg(self) -> str:
        return (
            f"postgresql+psycopg://"
            f"{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}"
            f"/{self.POSTGRES_DB}"
        )

    @property
    def POSTGRES_URL_asyncpg(self) -> str:
        return (
            f"postgresql+asyncpg://"
            f"{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}"
            f"/{self.POSTGRES_DB}"
        )

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / "env_files/.env.db",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )


class TasksSettings(BaseSettings):
    REDIS_HOST: str
    REDIS_PORT: int
    RABBITMQ_HOST: str
    RABBITMQ_PORT: int

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / "env_files/.env.tasks",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )


class LoggingSettings(BaseSettings):
    logging_level: int = logging.INFO

    model_config = SettingsConfigDict(
        case_sensitive=True,
    )


web_settings = WebSettings()  # type: ignore
database_settings = DatabaseSettings()  # type: ignore
tasks_settings = TasksSettings()  # type: ignore
logging_settings = LoggingSettings()
