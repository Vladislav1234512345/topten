from fastapi import Depends, HTTPException, Cookie
from sqlmodel import select
from starlette import status
from fastapi.security import OAuth2PasswordBearer

from exceptions import (
    invalid_email_exception,
    invalid_access_token_exception,
    refresh_token_not_found_exception,
    invalid_refresh_token_exception, expired_token_exception
)
from .utils import decode_jwt
from jwt.exceptions import InvalidTokenError, ExpiredSignatureError
from models import User
from database import AsyncSessionDep
from typing import Annotated, Any
from config import jwt_settings


oauth2_schema = OAuth2PasswordBearer(tokenUrl="/api/v1/jwt/login")


def get_current_access_token_payload(
        token: str = Depends(oauth2_schema)
) -> dict[str, Any]:
    try:
        payload: dict[str, Any] = decode_jwt(token=token)
    except ExpiredSignatureError:
        raise expired_token_exception
    except InvalidTokenError:
        raise invalid_access_token_exception
    return payload


def get_current_refresh_token_payload(refresh_token: Annotated[str | None, Cookie()]) -> dict[str, Any]:
    if refresh_token is None:
        raise refresh_token_not_found_exception
    try:
        payload: dict[str, Any] = decode_jwt(token=refresh_token)
    except ExpiredSignatureError:
        raise expired_token_exception
    except InvalidTokenError:
        raise invalid_refresh_token_exception
    return payload


def validate_token_type(
        payload: dict[str, Any],
        token_type: str
) -> bool:
    current_token_type = str(payload.get("type"))
    if current_token_type == token_type:
        return True

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=f"Неверный тип токена {current_token_type!r}, ожидался {token_type!r}",
    )


async def get_user_by_token_uid(
    session: AsyncSessionDep,
    payload: dict[str, Any]
) -> User:
    user_id: int = int(payload.get("uid"))
    statement = select(User).filter_by(id=user_id)
    try:
        result = await session.execute(statement)
    except:
        raise invalid_email_exception
    user = result.scalar()

    if not user:
        raise invalid_email_exception

    return user


class UserGetterFromAccessToken:
    async def __call__(
        self,
        session: AsyncSessionDep,
        payload: dict[str, Any] = Depends(get_current_access_token_payload)
    ) -> User:
        validate_token_type(payload=payload, token_type=jwt_settings.jwt_access_token_type)
        return await get_user_by_token_uid(session=session, payload=payload)


class UserGetterFromRefreshToken:
    async def __call__(
        self,
        session: AsyncSessionDep,
        payload: dict[str, Any] = Depends(get_current_refresh_token_payload)
    ) -> User:
        validate_token_type(payload=payload, token_type=jwt_settings.jwt_refresh_token_type)
        return await get_user_by_token_uid(session=session, payload=payload)


get_current_auth_user_for_access = UserGetterFromAccessToken()
get_current_auth_user_for_refresh = UserGetterFromRefreshToken()

