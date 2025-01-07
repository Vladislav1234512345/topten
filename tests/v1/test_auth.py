from fastapi.testclient import TestClient
from pydantic import BaseModel

from src.database import async_session_factory
from src.models import UserModel
from src.schemas import UserSchema
from src.v1.auth import router
from src.utils import create_user, select_user
from src.v1.auth.exceptions import current_user_yet_exists_exception
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



@pytest.mark.asyncio
async def test_is_user_auth() -> None:
    # email = "antonkutorov@gmail.com"
    # password = "qwerty1234"
    # first_name = "Vladislav"
    # user = await select_user_mock(email=email)
    # logger.info(f"{user=}")
    # if user:
    #     logger.info(f'Пользователь с почтой {email} уже существует.')
    # else:
    #     logger.info(f'Пользователь с почтой {email} не существует!')
    #     user = await create_user_mock(email=email, password=password, first_name=first_name)
    #     logger.info(f"{user=}")

    now = datetime.datetime.now()
    access_token = create_access_token_mock(user=UserSchema(id=1, email="antonkutorov@gmail.com", first_name="Vladislav", is_admin=False, is_stuff=False, is_active=True, created_at=now, updated_at=now))
    authorization_header = f"{jwt_settings.access_token_type} {access_token}"
    logger.info(f"authorization_header = {authorization_header}")
    client.headers['Authorization'] = authorization_header
    response = client.get('/auth/protected')
    assert response.status_code == 200
    logger.info(f"{response.json()=}")
    assert response.json()