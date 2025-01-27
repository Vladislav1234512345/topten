from starlette.responses import JSONResponse
from starlette import status


user_week_day_is_updated_response = JSONResponse(
    content="День недели пользователя был успешно обновлен.",
    status_code=status.HTTP_200_OK,
)
user_week_day_is_deleted_response = JSONResponse(
    content="День недели пользователя был успешно удален.",
    status_code=status.HTTP_200_OK,
)
user_week_day_is_created_response = JSONResponse(
    content="День недели пользователя был успешно создан.",
    status_code=status.HTTP_201_CREATED,
)
