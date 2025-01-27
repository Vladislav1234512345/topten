from starlette.responses import JSONResponse
from starlette import status


user_vacation_time_is_updated_response = JSONResponse(
    content="Отпуск пользователя по времени был успешно обновлен.",
    status_code=status.HTTP_200_OK,
)
user_vacation_time_is_deleted_response = JSONResponse(
    content="Отпуск пользователя по времени был успешно удален.",
    status_code=status.HTTP_200_OK,
)
user_vacation_time_is_created_response = JSONResponse(
    content="Отпуск пользователя по времени был успешно создан.",
    status_code=status.HTTP_201_CREATED,
)
