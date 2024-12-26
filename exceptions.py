from fastapi import HTTPException
from starlette import status

current_user_yet_exists_exception = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="Пользователь с такой почтой уже существует!"
)
invalid_password_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Неверный пароль!"
)
unauthorized_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Неудалось авторизоваться!"
)
invalid_email_exception = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="Пользователь с такой почтой не зарегистрирован!"
)
invalid_email_code_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Неверный код подтверждения!"
)
too_many_requests_exception = HTTPException(
    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
    detail="Слишком частые запросы. Попробуйте позже!"
)
invalid_access_token_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail=f"Неверный access токен!",
)
invalid_refresh_token_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail=f"Неверный refresh токен!",
)
refresh_token_not_found_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail=f"Строка с ключом 'refresh_token' отсутствует в cookies!"
)
expired_token_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail=f"Просроченный токен!"
)
