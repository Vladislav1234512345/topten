from starlette.exceptions import HTTPException
from starlette import status

update_user_break_exception = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="Не удалось обновить перерыв пользователя!",
)
user_break_not_found_exception = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND, detail="Перерыв пользователя не найден!"
)
users_breaks_not_found_exception = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND, detail="Перерывы пользователей не найдены!"
)
current_user_break_yet_exists_exception = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="Перерыв у пользователя уже существует!",
)
