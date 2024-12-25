from fastapi import APIRouter, Response, HTTPException, Depends, status
from fastapi.responses import JSONResponse
from redis.asyncio import Redis

from models import User
from database import AsyncSessionDep
from sqlmodel import select
from api.v1.sms.validators import validate_phone_number, validate_sms_code
from api.v1.sms.utils import get_redis_pool
from config import logger, jwt_settings
from .validators import get_current_auth_user_for_access, get_current_auth_user_for_refresh
from .utils import create_access_token, create_refresh_token
from config import cookies_settings


router = APIRouter()


@router.post('/auth')
async def auth(
    session: AsyncSessionDep,
    response: Response,
    redis_pool: Redis = Depends(get_redis_pool),
    phone_number: str = Depends(validate_phone_number),
    sms_code: str = Depends(validate_sms_code),
) -> JSONResponse:
    # validate_phone_number(phone_number=phone_number)
    # validate_sms_code(sms_code=sms_code)

    stored_code: str = await redis_pool.get(phone_number)

    logger.info(f"stored_code = {stored_code}")
    logger.info(f"sms_code = {sms_code}")

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

    access_token = create_access_token(user=user)
    refresh_token = create_refresh_token(user=user)

    response.headers['Authorization'] = f'{jwt_settings.access_token_type} {access_token}'

    response.set_cookie(
        key=cookies_settings.refresh_token_name,
        value=refresh_token,
        httponly=cookies_settings.httponly,
        samesite=cookies_settings.samesite,
        secure=cookies_settings.secure,
    )

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Авторизация прошла успешно"
        },
        headers=response.headers,
    )


@router.post('/refresh')
def refresh(
    response: Response,
    user: User = Depends(get_current_auth_user_for_refresh)
) -> JSONResponse:
    access_token = create_access_token(user=user)
    refresh_token = create_refresh_token(user=user)

    response.headers['Authorization'] = f'{jwt_settings.access_token_type} {access_token}'

    response.set_cookie(
        key=cookies_settings.refresh_token_name,
        value=refresh_token,
        httponly=cookies_settings.httponly,
        samesite=cookies_settings.samesite,
        secure=cookies_settings.secure,
    )

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Токены успешно обновлены",
        }
    )
