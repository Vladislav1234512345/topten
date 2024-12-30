from pydantic_settings import BaseSettings, SettingsConfigDict

from container import BASE_DIR


class DatabaseSettings(BaseSettings):
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    POSTGRES_PORT: str
    POSTGRES_DB: str

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / 'env_files/.env.db',
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


class TasksSettings(BaseSettings):
    REDIS_HOST: str
    REDIS_PORT: int
    RABBITMQ_HOST: str
    RABBITMQ_PORT: int

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / 'env_files/.env.tasks',
        env_file_encoding='utf-8',
        case_sensitive=False
    )


