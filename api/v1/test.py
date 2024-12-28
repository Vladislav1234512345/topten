from asyncio import get_event_loop
from redis.asyncio import Redis

from api.v1 import router as v1_router
from fastapi.testclient import TestClient

from config import logger, tasks_settings, jwt_settings, cookies_settings

import pytest


# Фикстура для цикла событий
@pytest.fixture(scope="function")
def event_loop():
    loop = get_event_loop()
    yield loop
    loop.close()


client = TestClient(app=v1_router)


async def func_test_refresh_tokens():
    response = client.post('/v1/jwt/refresh')

    assert response.status_code == 200
    assert response.json() == {"message": "Токены успешно обновлены."}


async def func_test_send_email(email: str, password: str) -> None:
    response = client.post('/v1/email/verification-code', json={"email": email, "password": password})

    assert response.status_code == 200
    assert response.json() == {"message": "Сообщение с кодом верификации успешно отправлено."}


async def func_test_signup(email: str, password: str, first_name: str, email_code: str) -> None:
    signup_json = {
        "email": email,
        "password": password,
        "first_name": first_name,
        "email_code": email_code
    }

    response = client.post('/v1/auth/signup', json=signup_json)

    assert response.status_code == 201
    assert response.json() == {"message": "Регистрация прошла успешно."}
    assert response.headers.get("authorization")

    logger.info(f"authorization = {response.headers.get("authorization")}")


async def func_test_login(email: str, password: str, email_code: str) -> None:
    login_json = {
        "email": email,
        "password": password,
        "email_code": email_code
    }

    response = client.post('/v1/auth/login', json=login_json)

    assert response.status_code == 200
    assert response.json() == {"message": "Авторизация прошла успешно."}
    assert response.headers.get("authorization")

    logger.info(f"authorization = {response.headers.get("authorization")}")



@pytest.mark.asyncio
async def test_send_email_code_than_signup_than_login_than_refresh_tokens():
    email = "antonkutorov@gmail.com"
    password = "qwerty1234"

    # await func_test_send_email(email=email, password=password)
    #
    # email_code = str(input("Введите код: "))
    #
    # logger.info(f"email_code = {email_code}")
    #
    # await func_test_signup(
    #     email=email,
    #     password="qwerty1234",
    #     first_name="Vladislav",
    #     email_code=email_code
    # )
    #
    # assert client.cookies.get(cookies_settings.refresh_token_name)
    #
    # logger.info(f"refresh_token = {client.cookies.get(cookies_settings.refresh_token_name)}")


    # # Login
    # await func_test_send_email(email=email, password=password)
    #
    # email_code = str(input("Введите код: "))
    #
    # logger.info(f"email_code = {email_code}")
    #
    # await func_test_login(
    #     email=email,
    #     password=password,
    #     email_code=email_code
    # )
    #
    # assert client.cookies.get(cookies_settings.refresh_token_name)
    #
    # logger.info(f"refresh_token = {client.cookies.get(cookies_settings.refresh_token_name)}")

    client.cookies.set(name="refresh_token", value="eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0eXBlIjoicmVmcmVzaCIsInVpZCI6MSwic3ViIjoiYW50b25rdXRvcm92QGdtYWlsLmNvbSIsIm5hbWUiOiJWbGFkaXNsYXYiLCJpYXQiOjE3MzU0MDk2MTQsImV4cCI6MTczNjAxNDQxNH0.U_CXuDl4plKeBrM0g_1UJTk4iQ7EjDC1ju40TnEr0LI3BhH0XAEdkWPr1his4_0uEEHw1NUlSuaqa0zd9fsj_ilfd4KD5B-HP61KeN4FWIo2QkRwyRI-RL30btxOHKWg2nehc3V5c3y92tu0zfWXr11EGWNgvXTVDjD5ZBtnObQbZ0pIzWsojI_oLjI_UE3hoV8o0T1ifP-2rDrNErWWueboc7teKnDNsouw5DFVsloG_-UuwhxOzPC8RYFx4oUTxJyAb5x8ZiPMvEe5QtuRePacG8B5tuGwoDgcYamk2cUQ77BRboUt4PoaEhn-pY73TLPh8GnFL2H1OeXX9zNL3g")

    await func_test_refresh_tokens()