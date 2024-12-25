from fastapi import APIRouter, HTTPException, Depends
from starlette.responses import JSONResponse
from starlette import status
from redis.asyncio import Redis

from models import User
from database import AsyncSessionDep
from sqlmodel import select
from api.v1.sms.validators import validate_phone_number, validate_sms_code
from api.v1.sms.utils import get_redis_pool
from .validators import get_current_auth_user_for_access, get_current_auth_user_for_refresh
from .utils import set_tokens_in_response



router = APIRouter()


@router.post('/auth')
async def auth(
    session: AsyncSessionDep,
    redis_pool: Redis = Depends(get_redis_pool),
    phone_number: str = Depends(validate_phone_number),
    sms_code: str = Depends(validate_sms_code),
) -> JSONResponse:

    stored_code: str = await redis_pool.get(phone_number)

    if stored_code != sms_code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Неверный код подтверждения",
        )

    unauthorized_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Неудалось авторизоваться"
    )

    statement = select(User).filter_by(phone_number=phone_number)
    try:
        result = await session.execute(statement)
    except:
        raise unauthorized_exception
    user = result.scalar()

    if not user:
        raise unauthorized_exception

    response: JSONResponse = JSONResponse(
        content={"message": "Авторизация прошла успешно"},
        status_code=status.HTTP_200_OK
    )

    return set_tokens_in_response(response=response, user=user)


@router.post('/refresh')
def refresh(
    user: User = Depends(get_current_auth_user_for_refresh)
) -> JSONResponse:

    response: JSONResponse = JSONResponse(
        content={"message": "Токены успешно обновлены"},
        status_code=status.HTTP_200_OK
    )

    return set_tokens_in_response(response=response, user=user)
