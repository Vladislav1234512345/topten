from fastapi import HTTPException
from starlette import status

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
