from starlette.responses import JSONResponse
from starlette import status


application_is_updated_response = JSONResponse(
    content="Заявление пользователя на услугу было успешно обновлено.",
    status_code=status.HTTP_200_OK,
)
application_is_deleted_response = JSONResponse(
    content="Заявление пользователя на услугу было успешно удалено.",
    status_code=status.HTTP_200_OK,
)
application_is_created_response = JSONResponse(
    content="Заявление пользователя на услугу было успешно создано.",
    status_code=status.HTTP_201_CREATED,
)
