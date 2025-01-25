from starlette.responses import JSONResponse
from starlette import status


profile_is_updated_response = JSONResponse(
    content="Профиль был успешно обновлен.", status_code=status.HTTP_200_OK
)
