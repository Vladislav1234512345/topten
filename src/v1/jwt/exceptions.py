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
    detail=f"Строка с ключом 'refresh_token' отсутствует в cookies!"
)
expired_token_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail=f"Просроченный токен!"
)
