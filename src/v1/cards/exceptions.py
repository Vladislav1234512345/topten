from starlette.exceptions import HTTPException
from starlette import status

current_user_card_yet_exists_exception = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="У пользователя уже существуют карточка с данной деятельностью!",
)
update_user_card_exception = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="Не удалось обновить карточку пользователя!",
)
user_card_not_found_exception = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND, detail="Карточка пользователя не найдена!"
)
users_cards_not_found_exception = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND, detail="Карточки пользователя не найдены!"
)
