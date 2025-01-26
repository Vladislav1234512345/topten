from starlette import status
from starlette.exceptions import HTTPException

profile_not_found_exception = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND, detail="Профиль не найден!"
)
profiles_not_found_exception = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND, detail="Профили не найдены!"
)
update_profile_exception = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="Не удалось обновить профиль пользователя!",
)
