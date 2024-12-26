from fastapi import HTTPException
from starlette import status


invalid_email_code_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Неверный код подтверждения"
)