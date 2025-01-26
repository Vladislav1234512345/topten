from starlette.responses import JSONResponse
from starlette import status


profile_is_updated_response = JSONResponse(
    content="Профиль был успешно обновлен.", status_code=status.HTTP_200_OK
)
profile_is_deleted_response = JSONResponse(
    content="Профиль был успешно удален.", status_code=status.HTTP_200_OK
)
profile_is_created_response = JSONResponse(
    content="Профиль был успешно создан.", status_code=status.HTTP_201_CREATED
)
