from starlette.responses import JSONResponse
from starlette import status


verification_code_email_response = JSONResponse(
    status_code=status.HTTP_200_OK,
    content={"message": "Сообщение с кодом верификации успешно отправлено."},
)
reset_password_email_response = JSONResponse(
    status_code=status.HTTP_200_OK,
    content={"message": "Сообщение для сброса пароля успешно отправлено."},
)
