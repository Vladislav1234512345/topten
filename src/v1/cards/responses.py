from starlette.responses import JSONResponse
from starlette import status


user_card_is_updated_response = JSONResponse(
    content="Карточка пользователя была успешно обновлена.",
    status_code=status.HTTP_200_OK,
)
user_card_is_deleted_response = JSONResponse(
    content="Карточка пользователя была успешно удалена.",
    status_code=status.HTTP_200_OK,
)
user_card_is_created_response = JSONResponse(
    content="Карточка пользователя была успешно создана.",
    status_code=status.HTTP_201_CREATED,
)
