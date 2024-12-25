import jwt
from config import jwt_settings
from datetime import timedelta, datetime, UTC
from models import User
from fastapi import Response
from config import cookies_settings


def encode_jwt(
    payload: dict,
    expire_timedelta: timedelta,
    private_key: str = jwt_settings.private_key_path.read_text(),
    algorithm: str = jwt_settings.algorithm,
) -> str:
    to_encode = payload.copy()
    now: datetime = datetime.now(UTC)
    expire: datetime = now + expire_timedelta
    to_encode.update(iat=now, exp=expire)
    encoded_jwt = jwt.encode(payload=to_encode, key=private_key, algorithm=algorithm)

    return encoded_jwt


def decode_jwt(
    token: str | bytes,
    public_key: str = jwt_settings.public_key_path.read_text(),
    algorithm: str = jwt_settings.algorithm
) -> dict:
    decoded_jwt = jwt.decode(jwt=token, key=public_key, algorithm=algorithm)

    return decoded_jwt


def create_access_token(user: User) -> str:
    jwt_payload_access_token = {
        "type": jwt_settings.jwt_access_token_type,
        "sub": user.id,
        "first_name": user.first_name,
    }

    access_token = encode_jwt(
        payload=jwt_payload_access_token,
        expire_timedelta=jwt_settings.access_token_expire_minutes,
    )

    return access_token


def create_refresh_token(user: User) -> str:
    jwt_payload_refresh_token = {
        "type": jwt_settings.jwt_refresh_token_type,
        "sub": user.id,
    }

    refresh_token = encode_jwt(
        payload=jwt_payload_refresh_token,
        expire_timedelta=jwt_settings.refresh_token_expire_days,
    )

    return refresh_token


def set_tokens(response: Response, user: User) -> Response:
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

    return response