from fastapi import HTTPException
from starlette import status

invalid_reset_password_key_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED, detail="Неверный ключ для сброса пароля!"
)
current_profile_yet_exists_exception = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="Профиль с такой почтой уже существует!",
)
