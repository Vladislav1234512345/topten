from fastapi import Depends, HTTPException, Cookie, Header
from sqlalchemy import select
from starlette import status
from fastapi.security import OAuth2PasswordBearer

from src.exceptions import (
    user_not_found_exception,
    user_is_not_admin_exception,
    user_is_not_stuff_exception,
)
from .exceptions import (
    invalid_access_token_exception,
    invalid_refresh_token_exception,
    refresh_token_not_found_exception,
    expired_token_exception,
    access_token_not_found_exception,
)
from .utils import decode_jwt
from jwt.exceptions import InvalidTokenError, ExpiredSignatureError
from src.schemas import UserSchema
from src.database import AsyncSessionDep
from typing import Annotated, Any
from .config import jwt_settings
from src.utils import select_user
import logging
from src.container import configure_logging
from src.config import logging_settings

logger = logging.getLogger(__name__)
configure_logging(level=logging_settings.logging_level)


oauth2_schema = OAuth2PasswordBearer(tokenUrl="/src/v1/jwt/login")


def get_current_access_token_payload(
    authorization: Annotated[str | None, Header()]
) -> dict[str, Any]:
    try:
        if authorization is None:
            logger.warning("Access token not found.")
            raise access_token_not_found_exception
        access_token = authorization.split(jwt_settings.access_token_type)[-1].strip()
        payload: dict[str, Any] = decode_jwt(token=access_token)
    except ExpiredSignatureError:
        logger.warning("Expired access token.")
        raise expired_token_exception
    except InvalidTokenError:
        logger.warning("Invalid access token.")
        raise invalid_access_token_exception
    return payload


def get_current_refresh_token_payload(
    refresh_token: Annotated[str | None, Cookie()]
) -> dict[str, Any]:
    if refresh_token is None:
        logger.warning("Refresh token not found.")
        raise refresh_token_not_found_exception
    try:
        payload: dict[str, Any] = decode_jwt(token=refresh_token)
    except ExpiredSignatureError:
        logger.warning("Expired refresh token.")
        raise expired_token_exception
    except InvalidTokenError:
        logger.warning("Invalid refresh token.")
        raise invalid_refresh_token_exception
    return payload


def validate_token_type(payload: dict[str, Any], token_type: str) -> bool:
    current_token_type = str(payload.get("type"))
    if current_token_type == token_type:
        return True
    logger.error(
        "Incorrect type token, expected token type: %r, received token type: %r",
        token_type,
        current_token_type,
    )
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=f"Неверный тип токена {current_token_type!r}, ожидался {token_type!r}",
    )


def validate_token_admin(payload: dict[str, Any]) -> bool:
    is_user_admin = bool(payload.get("admin"))
    if not is_user_admin:
        logger.warning("User is not admin.")
        raise user_is_not_admin_exception
    return True


def validate_token_stuff(payload: dict[str, Any]) -> bool:
    is_user_stuff = bool(payload.get("stuff"))
    if not is_user_stuff:
        logger.warning("User is not stuff.")
        raise user_is_not_stuff_exception

    return True


async def get_user_by_token_uid(
    session: AsyncSessionDep, payload: dict[str, Any]
) -> UserSchema:

    try:
        user_id = int(payload.get("uid"))  # type: ignore
    except ValueError:
        logger.warning("User not found by uid in token.")
        raise user_not_found_exception

    user = await select_user(session=session, id=user_id)

    if not user:
        logger.warning("User not found by uid in token.")
        raise user_not_found_exception

    return user


class UserGetterFromAccessToken:
    async def __call__(
        self,
        session: AsyncSessionDep,
        payload: dict[str, Any] = Depends(get_current_access_token_payload),
    ) -> UserSchema:
        validate_token_type(
            payload=payload, token_type=jwt_settings.jwt_access_token_type
        )
        return await get_user_by_token_uid(session=session, payload=payload)


class UserGetterFromRefreshToken:
    async def __call__(
        self,
        session: AsyncSessionDep,
        payload: dict[str, Any] = Depends(get_current_refresh_token_payload),
    ) -> UserSchema:
        validate_token_type(
            payload=payload, token_type=jwt_settings.jwt_refresh_token_type
        )
        return await get_user_by_token_uid(session=session, payload=payload)


class AdminUserGetterFromAccessToken:
    async def __call__(
        self,
        session: AsyncSessionDep,
        payload: dict[str, Any] = Depends(get_current_access_token_payload),
    ) -> UserSchema:
        validate_token_type(
            payload=payload, token_type=jwt_settings.jwt_access_token_type
        )
        validate_token_admin(payload=payload)
        return await get_user_by_token_uid(session=session, payload=payload)


class StuffUserGetterFromAccessToken:
    async def __call__(
        self,
        session: AsyncSessionDep,
        payload: dict[str, Any] = Depends(get_current_access_token_payload),
    ) -> UserSchema:
        validate_token_type(
            payload=payload, token_type=jwt_settings.jwt_access_token_type
        )
        validate_token_stuff(payload=payload)
        return await get_user_by_token_uid(session=session, payload=payload)


get_current_user_with_access_token = UserGetterFromAccessToken()
get_current_user_with_refresh_token = UserGetterFromRefreshToken()
get_current_admin_user_with_access_token = AdminUserGetterFromAccessToken()
get_current_stuff_user_with_access_token = StuffUserGetterFromAccessToken()
