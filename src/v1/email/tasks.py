import smtplib
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Optional

from src.config import logging_settings, web_settings
from src.container import configure_logging
from src.worker import app
from src.v1.email.config import email_settings
import logging


logger = logging.getLogger(__name__)
configure_logging(level=logging_settings.logging_level)


@app.task  # type: ignore
def send_email_reset_password(receiver_email: str, key: str) -> None:
    subject = "Сброс пароля"
    body = f"Ваша ссылка для сброса пароля: {web_settings.CLIENT_DOMAIN_LINK}/reset-password/{key}"
    email_was_sent = send_email(
        receiver_email=receiver_email, subject=subject, body=body
    )
    if email_was_sent:
        logger.info(
            f"Reset password link was successfully sent to the email: %s",
            receiver_email,
        )
    else:
        logger.error(
            "An error occurred when sending the password reset link to the email: %s",
            receiver_email,
        )


@app.task  # type: ignore
def send_email_verification_code(receiver_email: str, code: str) -> None:
    subject = "Код авторизации"
    body = f"Ваш код подтверждения: {code}"
    email_was_sent = send_email(
        receiver_email=receiver_email, subject=subject, body=body
    )
    if email_was_sent:
        logger.info(
            f"Verification code was successfully sent to the email: %s", receiver_email
        )
    else:
        logger.error(
            "An error occurred when sending the verification code to the email: %s",
            receiver_email,
        )


@app.task  # type: ignore
def send_email(
    receiver_email: str, subject: str, body: str, attachment_path: Optional[str] = None
) -> bool:
    msg = MIMEMultipart()
    msg["From"] = email_settings.EMAIL_NAME
    msg["To"] = receiver_email
    msg["Subject"] = subject
    msg.attach(MIMEText(_text=body, _subtype="plain"))

    try:
        if attachment_path:
            with open(attachment_path, "rb") as attachment:
                application = MIMEBase(_maintype="application", _subtype="octet-stream")
                application.set_payload(payload=attachment.read())
                encoders.encode_base64(application)
                application.add_header(
                    "Content-Disposition",
                    f"attachment; filename={attachment_path.split("/")[-1]}",
                )
                msg.attach(application)
        logger.info(
            f"The attachment was successfully added to the email to %r", receiver_email
        )
    except Exception as e:
        logger.error(
            f"An error occurred when adding the attachment to the email to %r\n%s",
            receiver_email,
            e,
        )

    try:
        with smtplib.SMTP_SSL(
            host=email_settings.SMTP_HOST, port=email_settings.SMTP_PORT
        ) as server:
            server.login(
                user=email_settings.EMAIL_NAME,
                password=email_settings.EMAIL_APP_PASSWORD,
            )  # Log in to your email account
            text = msg.as_string()
            server.sendmail(email_settings.EMAIL_NAME, receiver_email, text)
            logger.info(f"Email was successfully sent to the email: %s", receiver_email)
            return True
    except Exception as e:
        logger.error(
            f"An error occurred when sending the email to the email: %s\n%s",
            receiver_email,
            e,
        )
        return False
