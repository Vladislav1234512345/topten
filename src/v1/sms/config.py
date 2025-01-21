from datetime import timedelta

from pydantic_settings import BaseSettings, SettingsConfigDict

from src.container import BASE_DIR


class SMSSettings(BaseSettings):
    SMS_API_KEY: str

    expire_time: timedelta = timedelta(minutes=30)
    verification_code_key: str = "sms_verification_code"
    reset_password_key: str = "sms_reset_password"
    sms_api_url: str = "https://smsc.kz/rest/send/"

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / "env_files/.env.sms",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="allow",
    )


sms_settings = SMSSettings()  # type: ignore
