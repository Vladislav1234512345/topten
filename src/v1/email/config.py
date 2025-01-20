from datetime import timedelta

from pydantic_settings import BaseSettings, SettingsConfigDict

from src.container import BASE_DIR


class EmailSettings(BaseSettings):
    EMAIL_NAME: str
    EMAIL_APP_PASSWORD: str
    SMTP_HOST: str
    SMTP_PORT: int

    expire_time: timedelta = timedelta(minutes=30)
    verification_code_key: str = "email_verification_code"
    reset_password_key: str = "email_reset_password"

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / "env_files/.env.email",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="allow",
    )


email_settings = EmailSettings()  # type: ignore
