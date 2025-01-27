from starlette.exceptions import HTTPException
from starlette import status

update_user_card_service_exception = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="Не удалось обновить услуги карточки пользователя!",
)
user_card_service_not_found_exception = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="Услуга карточки пользователя не найден!",
)
users_cards_services_not_found_exception = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="Услуги карточек пользователей не найдены!",
)
current_user_card_service_yet_exists_exception = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="Услуга карточки пользователя уже существует!",
)
create_user_card_service_forbidden_exception = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail="У вас нету прав создавать услугу для данной карточки пользователя!",
)
delete_user_card_service_forbidden_exception = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail="У вас нету прав удалять услугу для данной карточки пользователя!",
)
update_user_card_service_forbidden_exception = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail="У вас нету прав обновлять услугу для данной карточки пользователя!",
)
