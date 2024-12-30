from fastapi import APIRouter, Depends
from starlette.responses import JSONResponse
from starlette import status

from src.models import User
from .dependencies import get_current_auth_user_for_refresh
from .utils import set_tokens_in_response

router = APIRouter()


@router.post('/refresh')
def refresh(
    user: User = Depends(get_current_auth_user_for_refresh)
) -> JSONResponse:

    response: JSONResponse = JSONResponse(
        content={"message": "Токены успешно обновлены."},
        status_code=status.HTTP_200_OK
    )

    return set_tokens_in_response(response=response, user=user)



