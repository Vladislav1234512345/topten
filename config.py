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
        env_file=BASE_DIR / '.env.db',
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


class JWTSettings(BaseSettings):
    private_key_path: Path = BASE_DIR / "certs" / "jwt-private.pem"
    public_key_path: Path = BASE_DIR / "certs" / "jwt-public.pem"
    algorithm: str = 'RS256'
    access_token_expire_minutes: timedelta = timedelta(minutes=15)
    refresh_token_expire_days: timedelta = timedelta(days=7)

    model_config = SettingsConfigDict(case_sensitive=False)


class CookiesSettings(BaseSettings):
    access_token_name: str = "access_token"
    refresh_token_name: str = "refresh_token"
    httponly: bool = True
    samesite: Literal['lax', 'strict', 'none'] | None = 'lax'
    secure: bool = False

    model_config = SettingsConfigDict(case_sensitive=False)


class RedisSettings(BaseSettings):
    REDIS_HOST: str
    REDIS_PORT: str

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / '.env._redis',
        env_file_encoding='utf-8',
        case_sensitive=False
    )


class SMSSettings(BaseSettings):
    expire_time: timedelta = timedelta(minutes=5)

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / '.env.sms',
        env_file_encoding='utf-8',
        case_sensitive=False,
        extra='allow'
    )

database_settings = DatabaseSettings()

jwt_settings = JWTSettings()

cookies_settings = CookiesSettings()

redis_settings = RedisSettings()

sms_settings = SMSSettings()
