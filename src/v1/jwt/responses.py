from starlette.responses import JSONResponse
from starlette import status


tokens_refresh_response = JSONResponse(
    content={"message": "Токены успешно обновлены."}, status_code=status.HTTP_200_OK
)
