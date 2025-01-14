from starlette.responses import JSONResponse
from starlette import status


signup_response = JSONResponse(
    content={"message": "Регистрация прошла успешно."},
    status_code=status.HTTP_201_CREATED,
)
login_response = JSONResponse(
    content={"message": "Авторизация прошла успешно."},
    status_code=status.HTTP_200_OK,
)
reset_password_response = JSONResponse(
    content={"message": "Пароль был успешно обновлен."},
    status_code=status.HTTP_200_OK,
)
