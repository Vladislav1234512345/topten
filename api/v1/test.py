from asyncio import sleep, get_event_loop
from redis.asyncio import Redis
from fastapi import Depends
from api.v1.email.utils import get_redis_pool

from api.v1 import router as v1_router
from fastapi.testclient import TestClient

from config import logger, redis_settings, jwt_settings, cookies_settings

import pytest


# Фикстура для цикла событий
@pytest.fixture(scope="function")
def event_loop():
    loop = get_event_loop()
    yield loop
    loop.close()


client = TestClient(app=v1_router)


async def func_test_send_email(email: str) -> None:
    response = client.post('/v1/email/send', json={"email": email})

    assert response.status_code == 200
    assert response.json() == {"message": "Код отправлен"}


async def func_test_signup(email: str, password: str, first_name: str, email_code: str) -> None:
    signup_json = {
        "email": email,
        "password": password,
        "first_name": first_name,
        "email_code": email_code
    }

    response = client.post('/v1/jwt/signup', json=signup_json)

    assert response.status_code == 201
    assert response.json() == {"message": "Регистрация прошла успешно"}
    assert response.headers.get("authorization")

    logger.info(f"authorization = {response.headers.get("authorization")}")


async def func_test_login(email: str, password: str, email_code: str) -> None:
    login_json = {
        "email": email,
        "password": password,
        "email_code": email_code
    }

    response = client.post('/v1/jwt/login', json=login_json)

    assert response.status_code == 200
    assert response.json() == {"message": "Авторизация прошла успешно"}
    assert response.headers.get("authorization")

    logger.info(f"authorization = {response.headers.get("authorization")}")



@pytest.mark.asyncio
async def test_send_email_code_than_signup_than_login_than_refresh_tokens():
    email="tolerantniy1234@gmail.com"
    redis_pool = Redis(host=redis_settings.REDIS_HOST, port=redis_settings.REDIS_PORT)

    await func_test_send_email(email=email)
    email_code_encoded: bytes = await redis_pool.get(email)
    await redis_pool.aclose()

    email_code: str = email_code_encoded.decode()

    logger.info(f"email_code = {email_code}")

    await func_test_signup(
        email=email,
        password="qwerty1234",
        first_name="Vladislav",
        email_code=email_code
    )

    assert client.cookies.get(cookies_settings.refresh_token_name)

    logger.info(f"refresh_token = {client.cookies.get(cookies_settings.refresh_token_name)}")


    # Login
    await func_test_send_email(email=email)

    email_code_encoded: bytes = await redis_pool.get(email)
    await redis_pool.aclose()

    email_code: str = email_code_encoded.decode()

    await func_test_login(
        email=email,
        password="qwerty1234",
        email_code=email_code
    )

    assert client.cookies.get(cookies_settings.refresh_token_name)

    logger.info(f"refresh_token = {client.cookies.get(cookies_settings.refresh_token_name)}")
