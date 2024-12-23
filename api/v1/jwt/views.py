from fastapi import APIRouter, Response, Depends
from .schemas import TokensInfoSchema
from .auth import validate_authorization
from .utils import encode_jwt
from models import User
from config import jwt_settings, cookies_settings


router = APIRouter()


@router.post('/auth', response_model=TokensInfoSchema)
def auth(
    response: Response,
    user: User = Depends(validate_authorization)
) -> TokensInfoSchema:
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

    return TokensInfoSchema(
        access_token=access_token,
        refresh_token=refresh_token,
    )