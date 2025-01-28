from starlette.exceptions import HTTPException
from starlette import status

current_user_card_review_yet_exists_exception = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="У пользователя уже существует обзор данной карточки пользователя!",
)
update_user_card_review_exception = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="Не удалось обновить обзор пользователя карточки пользователя!",
)
user_card_review_not_found_exception = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="Обзор пользователя на карточку пользователя не найден!",
)
users_cards_reviews_not_found_exception = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="Обзоры пользователей на карточки пользователей не найдены!",
)
