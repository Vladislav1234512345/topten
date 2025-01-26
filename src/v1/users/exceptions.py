from starlette.exceptions import HTTPException
from starlette import status

update_user_exception = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="Не удалось обновить пользователя!",
)
user_not_found_exception = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь не найден!"
)
users_not_found_exception = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND, detail="Пользователи не найдены!"
)
