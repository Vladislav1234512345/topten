from pydantic_settings import BaseSettings, SettingsConfigDict
from container import BASE_DIR


class WebSettings(BaseSettings):
    WEBAPP_HOST: str
    WEBAPP_PORT: int

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / 'env_files/.env',
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
    def POSTGRES_URL_psycopg(self):
        return (
            f"postgresql+psycopg://"
            f"{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}"
            f"/{self.POSTGRES_DB}"
        )

    @property
    def POSTGRES_URL_asyncpg(self):
        return (
            f"postgresql+asyncpg://"
            f"{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}"
            f"/{self.POSTGRES_DB}"
        )

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / 'env_files/.env.db',
        env_file_encoding="utf-8",
        case_sensitive=True,
    )


class TasksSettings(BaseSettings):
    REDIS_HOST: str
    REDIS_PORT: int
    RABBITMQ_HOST: str
    RABBITMQ_PORT: int

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / 'env_files/.env.tasks',
        env_file_encoding='utf-8',
        case_sensitive=True
    )


web_settings = WebSettings()
database_settings = DatabaseSettings()
tasks_settings = TasksSettings()
