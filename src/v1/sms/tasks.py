import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from src.config import logging_settings, web_settings
from src.container import configure_logging
from src.v1.email.config import email_settings
from src.worker import app
import logging


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
    msg = MIMEMultipart()
    msg["From"] = email_settings.EMAIL_NAME
    msg["To"] = receiver_phone_number
    msg["Subject"] = subject
    msg.attach(MIMEText(_text=body, _subtype="plain"))

    try:
        with smtplib.SMTP_SSL(
            host=email_settings.SMTP_HOST, port=email_settings.SMTP_PORT
        ) as server:
            server.login(
                user=email_settings.EMAIL_NAME,
                password=email_settings.EMAIL_APP_PASSWORD,
            )  # Log in to your email account
            text = msg.as_string()
            server.sendmail(email_settings.EMAIL_NAME, receiver_phone_number, text)
            logger.info(
                f"SMS was successfully sent to the phone number: %s",
                receiver_phone_number,
            )
            return True
    except Exception as e:
        logger.error(
            f"An error occurred when sending the sms to the phone number: %s\nError: %s",
            receiver_phone_number,
            e,
        )
        return False
