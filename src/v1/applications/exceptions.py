from starlette.exceptions import HTTPException
from starlette import status

current_application_yet_exists_exception = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="Данное заявление пользователя на услугу уже существует!",
)
update_application_exception = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="Не удалось обновить заявление пользователя на услугу!",
)
application_not_found_exception = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="Заявление пользователя на услугу не найдено!",
)
applications_not_found_exception = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="Заявления пользователей на услуги не найдены!",
)
update_application_forbidden_exception = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail="У вас нету прав обновлять заявление пользователя на услугу!",
)
