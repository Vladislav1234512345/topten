from fastapi import HTTPException
from starlette import status


unauthorized_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Неудалось авторизоваться"
)