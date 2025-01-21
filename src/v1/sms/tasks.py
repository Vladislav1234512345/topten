from src.config import logging_settings, web_settings
from src.container import configure_logging
from src.v1.sms.config import sms_settings
from src.worker import app
import logging
import httpx
import json


logger = logging.getLogger(__name__)
configure_logging(level=logging_settings.logging_level)


@app.task  # type: ignore
def send_sms_reset_password(receiver_phone_number: str, key: str) -> None:
    subject = "Сброс пароля"
    body = f"Ваша ссылка для сброса пароля: {web_settings.FRONTEND_LINK}/reset-password/{key}"
    sms_is_sent = send_sms(
        receiver_phone_number=receiver_phone_number, subject=subject, body=body
    )
    if sms_is_sent:
        logger.info(
            f"Reset password sms was successfully sent to the phone number: %s",
            receiver_phone_number,
        )
    else:
        logger.error(
            "An error occurred when sending the password reset sms to the phone number: %s",
            receiver_phone_number,
        )


@app.task  # type: ignore
def send_sms_verification_code(receiver_phone_number: str, code: str) -> None:
    subject = "Код авторизации"
    body = f"Ваш код подтверждения: {code}"
    sms_is_sent = send_sms(
        receiver_phone_number=receiver_phone_number, subject=subject, body=body
    )
    if sms_is_sent:
        logger.info(
            f"Verification code sms was successfully sent to the phone number: %s",
            receiver_phone_number,
        )
    else:
        logger.error(
            "An error occurred when sending the verification code sms to the phone number: %s",
            receiver_phone_number,
        )


@app.task  # type: ignore
def send_sms(receiver_phone_number: str, subject: str, body: str) -> bool:
    with httpx.Client() as client:
        response = client.post(
            url=sms_settings.sms_api_url,
            content=json.dumps(
                {
                    "apikey": sms_settings.SMS_API_KEY,
                    "phones": receiver_phone_number,
                    "mes": body,
                    "subj": subject,
                    "mms": True,
                }
            ),
        )

        if response.is_success:
            logger.info(
                f"SMS was successfully sent to the phone number: %s",
                receiver_phone_number,
            )
            return True
        else:
            logger.error(
                f"An error occurred when sending the sms to the phone number: %s\nError: %s",
                receiver_phone_number,
                response.text,
            )
            return False
