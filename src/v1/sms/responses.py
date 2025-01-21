from starlette.responses import JSONResponse
from starlette import status


verification_code_sms_response = JSONResponse(
    status_code=status.HTTP_200_OK,
    content={"message": "SMS Сообщение с кодом верификации успешно отправлено."},
)
reset_password_sms_response = JSONResponse(
    status_code=status.HTTP_200_OK,
    content={"message": "SMS Сообщение для сброса пароля успешно отправлено."},
)
