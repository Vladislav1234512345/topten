from starlette.exceptions import HTTPException
from starlette import status

update_user_exception = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="Не удалось обновить пользователя!",
)
