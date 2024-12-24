from fastapi import APIRouter, Response, Form, HTTPException, Depends
from starlette import status
from starlette.responses import JSONResponse

from .utils import encode_jwt
from models import User
from config import jwt_settings, cookies_settings
from database import AsyncSessionDep
from sqlmodel import select
from api.v1.sms.validators import validate_phone_number, validate_sms_code
from api.v1.sms.utils import get_redis_pool


router = APIRouter()


@router.post('/auth')
async def auth(
    session: AsyncSessionDep,
    redis_pool: Depends(get_redis_pool),
    response: Response,
    phone_number: str = Form(),
    sms_code: str = Form(),
) -> JSONResponse:
    validate_phone_number(phone_number=phone_number)
    validate_sms_code(sms_code=sms_code)

    stored_code = await redis_pool.get(phone_number)

    if not stored_code or stored_code.decode() != phone_number:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Неверный код подтверждения",
        )

    unauthorized_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Неудалось авторизоваться"
    )
    statement = select(User).filter_by(phone_number=phone_number)
    result = await session.execute(statement)
    user = result.scalar()

    if not user:
        raise unauthorized_exception

    jwt_payload = {
        "sub": user.id,
        "first_name": user.first_name,
    }

    access_token = encode_jwt(
        payload=jwt_payload,
        expire_timedelta=jwt_settings.access_token_expire_minutes,
    )
    refresh_token = encode_jwt(
        payload=jwt_payload,
        expire_timedelta=jwt_settings.refresh_token_expire_days,
    )

    response.headers['Authorization'] = f'Bearer {access_token}'

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
            "access_token": access_token,
            "refresh_token": refresh_token,
        }
    )
