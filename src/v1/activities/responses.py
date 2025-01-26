from starlette.responses import JSONResponse
from starlette import status


activity_is_updated_response = JSONResponse(
    content="Деятельность была успешно обновлена.", status_code=status.HTTP_200_OK
)
activity_is_deleted_response = JSONResponse(
    content="Деятельность была успешно удалена.", status_code=status.HTTP_200_OK
)
activity_is_created_response = JSONResponse(
    content="Деятельность была успешно создана.", status_code=status.HTTP_201_CREATED
)
