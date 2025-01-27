from starlette.responses import JSONResponse
from starlette import status


user_card_service_is_updated_response = JSONResponse(
    content="Услуга карточки пользователя была успешно обновлена.",
    status_code=status.HTTP_200_OK,
)
user_card_service_is_deleted_response = JSONResponse(
    content="Услуга карточки пользователя была успешно удалена.",
    status_code=status.HTTP_200_OK,
)
user_card_service_is_created_response = JSONResponse(
    content="Услуга карточки пользователя была успешно создана.",
    status_code=status.HTTP_201_CREATED,
)
