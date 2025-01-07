from datetime import timedelta

from pydantic_settings import BaseSettings, SettingsConfigDict

from src.container import BASE_DIR


class EmailSettings(BaseSettings):
    EMAIL_NAME: str
    EMAIL_APP_PASSWORD: str

    expire_time: timedelta = timedelta(minutes=2)
    verification_code_name: str = "code"
    reset_password_name: str = "password"

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / 'env_files/.env.email',
        env_file_encoding='utf-8',
        case_sensitive=True,
        extra='allow'
    )


email_settings = EmailSettings()
