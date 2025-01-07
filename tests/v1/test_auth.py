from fastapi.testclient import TestClient
from pydantic import BaseModel

from src.database import async_session_factory
from src.models import UserModel
from src.schemas import UserSchema
from src.v1.auth import router
from src.utils import create_user, select_user
from src.v1.auth.exceptions import current_user_yet_exists_exception
from src.v1.email.schemas import EmailPasswordFirstNameVerificationCodeSchema, EmailPasswordVerificationCodeSchema, \
    EmailTwoPasswordsSchema
from src.v1.jwt.config import jwt_settings
from src.v1.jwt.utils import encode_jwt, hash_password
from src.container import logger
import datetime

import pytest

client = TestClient(router)


def create_access_token_mock(user: UserSchema) -> str:
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


async def create_user_mock(email: str, password: str, first_name: str) -> UserSchema:
    logger.info(f"{email=}")
    async with async_session_factory() as session:
        user = await create_user(
            user=UserModel(
                email=email,
                password=hash_password(password),
                first_name=first_name
            ),
            session=session,
            exception=current_user_yet_exists_exception)
        logger.info(f"Пользователь с почтой {email} успешно создан.")
        return user


async def select_user_mock(**filters) -> UserSchema:
    async with async_session_factory() as session:
        return await select_user(session=session, **filters)


async def delete_user_mock(user: UserSchema):
    email = user.email
    async with async_session_factory() as session:
        session.delete(user)
        await session.commit()
        logger.info(f"Пользователь с почтой {email} успешно удален.")


async def test_refresh(user: UserSchema, is_active: bool = False) -> None:
    if not is_active:
        return None
    access_token = create_access_token_mock(user=user)
    authorization_header = f"{jwt_settings.access_token_type} {access_token}"
    logger.info(f"authorization_header = {authorization_header}")
    client.headers['Authorization'] = authorization_header
    response = client.get('/auth/protected')
    assert response.status_code == 200
    logger.info(f"{response.json()=}")
    assert response.json()


async def test_signup(user: EmailPasswordFirstNameVerificationCodeSchema, is_active: bool = False) -> None:
    if not is_active:
        return None

    response = client.post("/auth/signup", content=user.json())

    assert response.status_code == 201
    assert response.json() == {"message": "Регистрация прошла успешно."}


async def test_login(user: EmailPasswordVerificationCodeSchema, is_active: bool = False) -> None:
    if not is_active:
        return None

    response = client.post("/auth/login", content=user.json())

    assert response.status_code == 200
    assert response.json() == {"message": "Авторизация прошла успешно."}


async def test_reset_password(user: EmailTwoPasswordsSchema, key: str, is_active: bool = False) -> None:
    if not is_active:
        return None

    response = client.post(f"/auth/reset-password/{key}", content=user.json())

    assert response.status_code == 200
    assert response.json() == {"message": "Пароль был успешно обновлен."}


@pytest.mark.asyncio
async def test_is_user_auth() -> None:
    now = datetime.datetime.now()
    email = "antonkutorov@gmail.com"
    new_password_1 = "qwerty1234"
    new_password_2 = "qwerty1232"
    signup_password = "qwerty1234"
    first_name = "Vladislav"

    email_code = "909691"
    key = ""

    if not email_code:
        email_code = "SECRET"
    if not key:
        key = "KEY_CODE"

    await test_refresh(user=UserSchema(id=1, email=email, first_name=first_name, is_active=False, is_admin=False, is_stuff=False, created_at=now, updated_at=now), is_active=False)
    await test_signup(user=EmailPasswordFirstNameVerificationCodeSchema(email=email, first_name=first_name, password=signup_password, email_code=email_code), is_active=False)
    await test_login(user=EmailPasswordVerificationCodeSchema(email=email, password=signup_password, email_code=email_code), is_active=False)
    await test_reset_password(user=EmailTwoPasswordsSchema(email=email, password=new_password_1, password2=new_password_1), key=key, is_active=False)

