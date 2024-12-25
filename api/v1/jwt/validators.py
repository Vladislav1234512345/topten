from fastapi import Depends, HTTPException, status, Cookie
from fastapi.security import OAuth2PasswordBearer
from .utils import decode_jwt
from jwt import InvalidTokenError
from models import User
from database import AsyncSessionDep
from sqlmodel import select
from typing import Annotated
from datetime import datetime, UTC
from config import jwt_settings


oauth2_schema = OAuth2PasswordBearer(tokenUrl="/api/v1/jwt/auth")


def get_current_access_token_payload(
        token: str = Depends(oauth2_schema)
) -> dict:
    try:
        payload: dict = decode_jwt(token=token)
    except InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Неверный access токен: {e}",
        )
    return payload


def get_current_refresh_token_payload(refresh_token: Annotated[str | None, Cookie()]) -> dict:
    if refresh_token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"refresh_token отсутствует в cookies"
        )
    try:
        payload: dict = decode_jwt(token=refresh_token)
    except InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Неверный refresh токен: {e}",
        )
    return payload


def validate_token_type(
        payload: dict,
        token_type: str
) -> bool:
    current_token_type = str(payload.get("type"))
    if current_token_type == token_type:
        return True

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=f"Неверный тип токена {current_token_type!r}, ожидался {token_type!r}",
    )


def validate_token_expire(payload: dict) -> bool:
    current_token_exp: datetime = datetime(payload.get("exp"))
    datetime_now: datetime = datetime.now(UTC)
    if current_token_exp > datetime_now:
        return True

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=f"Просроченный токен ('exp' = {current_token_exp!r}, 'now = {datetime_now!r})"
    )


async def get_user_by_token_sub(
    session: AsyncSessionDep,
    payload: dict
) -> User:
    id: int = int(payload.get("sub"))
    unauthorized_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Неудалось авторизоваться"
    )
    statement = select(User).filter_by(id=id)
    try:
        result = await session.execute(statement)
    except:
        raise unauthorized_exception
    user = result.scalar()

    if not user:
        raise unauthorized_exception

    return user


class UserGetterFromAccessToken:
    async def __call__(
        self,
        session: AsyncSessionDep,
        payload: dict = Depends(get_current_access_token_payload)
    ) -> User:
        validate_token_type(payload=payload, token_type=jwt_settings.jwt_access_token_type)
        validate_token_expire(payload=payload)
        return await get_user_by_token_sub(session=session, payload=payload)


class UserGetterFromRefreshToken:
    async def __call__(
        self,
        session: AsyncSessionDep,
        payload: dict = Depends(get_current_refresh_token_payload)
    ) -> User:
        validate_token_type(payload=payload, token_type=jwt_settings.jwt_refresh_token_type)
        validate_token_expire(payload=payload)
        return await get_user_by_token_sub(session=session, payload=payload)


get_current_auth_user_for_access = UserGetterFromAccessToken()
get_current_auth_user_for_refresh = UserGetterFromRefreshToken()

