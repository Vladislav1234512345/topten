from fastapi import HTTPException
from starlette import status

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
    detail=f"'refresh_token' отсутствует в cookies!"
)
access_token_not_found_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail=f"'Authorization' заголовок с jwt токеном доступа отсутствует!"
)
expired_token_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail=f"Просроченный токен!"
)
forbidden_admin_available_exception = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail=f"Вы не являетесь админом сервиса!"
)
forbidden_stuff_available_exception = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail=f"Вы не являетесь работником сервиса!"
)
