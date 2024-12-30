from datetime import timedelta
from pathlib import Path
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict

from src.container import BASE_DIR


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
