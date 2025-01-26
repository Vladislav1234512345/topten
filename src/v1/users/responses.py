from starlette.responses import JSONResponse
from starlette import status


user_is_updated_response = JSONResponse(
    content="Пользователь был успешно обновлен.", status_code=status.HTTP_200_OK
)
user_is_deleted_response = JSONResponse(
    content="Пользователь был успешно удален.", status_code=status.HTTP_200_OK
)
user_is_created_response = JSONResponse(
    content="Пользователь был успешно создан.", status_code=status.HTTP_201_CREATED
)
