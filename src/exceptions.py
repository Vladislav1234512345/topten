from fastapi import HTTPException
from starlette import status
from starlette.exceptions import HTTPException


invalid_password_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED, detail="Неверный пароль!"
)
unauthorized_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED, detail="Неудалось авторизоваться!"
)
user_not_found_exception = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь не найден!"
)
invalid_email_code_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED, detail="Неверный код подтверждения!"
)
too_many_requests_exception = HTTPException(
    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
    detail="Слишком частые запросы. Попробуйте позже!",
)
invalid_email_exception = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail=f"Такой почты не существует!",
)
reset_user_password_exception = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="Не удалось обновить пароль пользователя!",
)
user_is_not_admin_exception = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail="Пользователь не является админом сервиса!",
)
user_is_not_stuff_exception = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail="Пользователь не является работником сервиса!",
)
different_passwords_exception = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST, detail="Пароли не совпадает!"
)
password_must_contain_a_digit_exception = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="Пароль должен содержать хотя бы 1 цифру!",
)
password_must_contain_an_uppercase_letter_exception = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="Пароль должен содержать хотя бы 1 заглавную букву!",
)
password_min_length_exception = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="Длина пароля должна быть минимум 8 символов!",
)
