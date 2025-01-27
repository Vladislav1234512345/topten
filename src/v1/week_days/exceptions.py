from starlette.exceptions import HTTPException
from starlette import status

update_user_week_day_exception = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="Не удалось обновить день недели пользователя!",
)
user_week_day_not_found_exception = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND, detail="День недели пользователя не найден!"
)
users_week_days_not_found_exception = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND, detail="Дни недели пользователей не найдены!"
)
current_user_week_day_yet_exists_exception = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="Данный день недели пользователя уже существует!",
)
