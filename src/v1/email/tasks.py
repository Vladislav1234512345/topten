import smtplib
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Optional

from src.container import logger
from src.worker import app
from src.v1.email.config import email_settings


@app.task  # type: ignore
def send_email_reset_password(receiver_email: str, key: str) -> None:
    subject = "Сброс пароля"
    body = f"Ваш ключ для сброса пароля: {key}"
    send_email(receiver_email=receiver_email, subject=subject, body=body)


@app.task  # type: ignore
def send_email_verification_code(receiver_email: str, code: str) -> None:
    subject = "Код авторизации"
    body = f"Ваш код подтверждения: {code}"
    send_email(receiver_email=receiver_email, subject=subject, body=body)


@app.task  # type: ignore
def send_email(
    receiver_email: str, subject: str, body: str, attachment_path: Optional[str] = None
) -> None:
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
    except:
        logger.error(
            f"Произошла ошибка в момент закрепления вложения в письмо на почту {receiver_email}"
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
            logger.info(f"Успешно было отправлено сообщение на почту {receiver_email}")
    except Exception as e:
        logger.error(
            f"Произошла ошибка отправки сообщения на почту {receiver_email}:\n{e}"
        )
