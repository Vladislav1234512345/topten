from starlette.exceptions import HTTPException
from starlette import status

update_activity_exception = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="Не удалось обновить деятельность!",
)
activity_not_found_exception = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND, detail="Деятельность не найдена!"
)
activities_not_found_exception = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND, detail="Деятельности не найдены!"
)
current_activity_yet_exists_exception = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="Такая деятельность уже существует!",
)
