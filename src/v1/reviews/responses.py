from starlette.responses import JSONResponse
from starlette import status


user_card_review_is_updated_response = JSONResponse(
    content="Обзор пользователя на карточку пользователя был успешно обновлен.",
    status_code=status.HTTP_200_OK,
)
user_card_review_is_deleted_response = JSONResponse(
    content="Обзор пользователя на карточку пользователя был успешно удален.",
    status_code=status.HTTP_200_OK,
)
user_card_review_is_created_response = JSONResponse(
    content="Обзор пользователя на карточку пользователя был успешно создан.",
    status_code=status.HTTP_201_CREATED,
)
