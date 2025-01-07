import bcrypt
import jwt
from src.v1.jwt.config import jwt_settings, cookies_settings
from datetime import timedelta, datetime, UTC
from src.schemas import UserSchema
from starlette.responses import JSONResponse
from typing import Any


def encode_jwt(
    payload: dict[str, Any],
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
) -> dict[str, Any]:
    decoded_jwt: dict[str, Any] = jwt.decode(jwt=token, key=public_key, algorithms=[algorithm])
    return decoded_jwt


def create_access_token(user: UserSchema) -> str:
    jwt_payload_access_token = {
        "type": jwt_settings.jwt_access_token_type,
        "uid": user.id,
        "sub": user.email,
        "name": user.first_name,
        "admin": user.is_admin,
        "stuff": user.is_stuff,
    }

    access_token = encode_jwt(
        payload=jwt_payload_access_token,
        expire_timedelta=jwt_settings.access_token_expire_minutes,
    )

    return access_token


def create_refresh_token(user: UserSchema) -> str:
    jwt_payload_refresh_token = {
        "type": jwt_settings.jwt_refresh_token_type,
        "uid": user.id,
        "sub": user.email,
        "name": user.first_name,
        "admin": user.is_admin,
        "stuff": user.is_stuff
    }

    refresh_token = encode_jwt(
        payload=jwt_payload_refresh_token,
        expire_timedelta=jwt_settings.refresh_token_expire_days,
    )

    return refresh_token


def set_tokens_in_response(response: JSONResponse, user: UserSchema) -> JSONResponse:
    access_token: str = create_access_token(user=user)
    refresh_token: str = create_refresh_token(user=user)

    response.headers["Authorization"] = f"{jwt_settings.access_token_type} {access_token}"

    response.set_cookie(
        key=cookies_settings.refresh_token_name,
        value=refresh_token,
        httponly=cookies_settings.httponly,
        samesite=cookies_settings.samesite,
        secure=cookies_settings.secure,
    )

    return response


def hash_password(password: str) -> bytes:
    salt: bytes = bcrypt.gensalt()
    return bcrypt.hashpw(password=password.encode(), salt=salt)


def validate_password(password: str, hashed_password: bytes) -> bool:
    return bcrypt.checkpw(password=password.encode(), hashed_password=hashed_password)