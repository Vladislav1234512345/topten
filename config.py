from pydantic_settings import BaseSettings, SettingsConfigDict
from os.path import dirname
from pathlib import Path
from datetime import timedelta
from typing import Literal
import logging

logger = logging.getLogger(__name__)


BASE_DIR = Path(dirname(__file__))


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


class JWTSettings(BaseSettings):
    private_key_path: Path = BASE_DIR / "certs" / "jwt-private.pem"
    public_key_path: Path = BASE_DIR / "certs" / "jwt-public.pem"
    algorithm: str = 'RS256'
    access_token_expire_minutes: timedelta = timedelta(minutes=15)
    refresh_token_expire_days: timedelta = timedelta(days=7)
    access_token_type: str = "Bearer"
    jwt_access_token_type: str = "access"
    jwt_refresh_token_type: str = "refresh"

    model_config = SettingsConfigDict(case_sensitive=False)


class CookiesSettings(BaseSettings):
    refresh_token_name: str = "refresh_token"
    httponly: bool = True
    samesite: Literal['lax', 'strict', 'none'] | None = 'lax'
    secure: bool = False

    model_config = SettingsConfigDict(case_sensitive=False)


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


class EmailSettings(BaseSettings):
    EMAIL_NAME: str
    EMAIL_APP_PASSWORD: str

    expire_time: timedelta = timedelta(minutes=5)
    verification_code_name: str = "code"
    reset_password_name: str = "password"

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / 'env_files/.env.email',
        env_file_encoding='utf-8',
        case_sensitive=False,
        extra='allow'
    )

database_settings = DatabaseSettings()

jwt_settings = JWTSettings()

cookies_settings = CookiesSettings()

tasks_settings = TasksSettings()

email_settings = EmailSettings()
