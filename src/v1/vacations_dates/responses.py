from starlette.responses import JSONResponse
from starlette import status


user_vacation_date_is_updated_response = JSONResponse(
    content="Отпуск пользователя по дате был успешно обновлен.",
    status_code=status.HTTP_200_OK,
)
user_vacation_date_is_deleted_response = JSONResponse(
    content="Отпуск пользователя по дате был успешно удален.",
    status_code=status.HTTP_200_OK,
)
user_vacation_date_is_created_response = JSONResponse(
    content="Отпуск пользователя по дате был успешно создан.",
    status_code=status.HTTP_201_CREATED,
)
