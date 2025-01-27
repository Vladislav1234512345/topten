from starlette.exceptions import HTTPException
from starlette import status

update_user_vacation_time_exception = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="Не удалось обновить отпуск пользователя по времени!",
)
user_vacation_time_not_found_exception = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="Отпуск пользователя по времени не найден!",
)
users_vacations_times_not_found_exception = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="Отпуска пользователей по времени не найдены!",
)
current_user_vacation_time_yet_exists_exception = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="Данный отпуск пользователя по времени уже существует!",
)
