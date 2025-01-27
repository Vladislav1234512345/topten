from starlette.exceptions import HTTPException
from starlette import status

update_user_vacation_date_exception = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="Не удалось обновить отпуск пользователя по дате!",
)
user_vacation_date_not_found_exception = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="Отпуск пользователя по дате не найден!",
)
users_vacations_dates_not_found_exception = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="Отпуска пользователей по датам не найдены!",
)
current_user_vacation_date_yet_exists_exception = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="Данный отпуск пользователя по дате уже существует!",
)
