from asyncio import sleep, get_event_loop
from redis.asyncio import Redis
from fastapi import Depends
from api.v1.sms.utils import get_redis_pool

from api.v1 import router as v1_router
from fastapi.testclient import TestClient

from config import logger, redis_settings

import pytest


# Фикстура для цикла событий
@pytest.fixture(scope="function")
def event_loop():
    loop = get_event_loop()
    yield loop
    loop.close()


client = TestClient(app=v1_router)
async def func_test_send_sms_code(phone_number: str) -> None:
    logger.debug("func_test_send_sms_send function is running")

    send_sms_code_data: dict = {'phone_number': phone_number}

    logger.info(f"send_sms_code_data: {send_sms_code_data}")

    response = client.post('/v1/sms/send', data=send_sms_code_data)
    assert response.status_code == 200
    assert response.json() == {"message": "Код отправлен"}


async def func_test_auth(phone_number: str, sms_code: str) -> None:
    logger.debug("func_test_auth function is running")
    logger.info(f"phone_number = {phone_number}, sms_code = {sms_code}")

    auth_data: dict = {
        'phone_number': phone_number,
        'sms_code': sms_code,
    }

    logger.info(f"auth_data: {auth_data}")

    response = client.post(url='/v1/jwt/auth', data=auth_data)

    logger.info(f"response.headers: {response.headers}")

    assert response.status_code == 200
    assert response.json() == {'message': 'Авторизация прошла успешно'}

    str(response.json().get("access_token"))


async def func_test_refresh() -> None:
    response = client.post(url='/v1/jwt/refresh')

    assert response.status_code == 200
    assert response.json() == {"message": "Токены успешно обновлены"}


async def func_test_send_sms_code_and_auth(
        phone_number: str,
        sleep_time: int = 0,
) -> None:
    if sleep_time < 0:
        raise TimeoutError("sleep_time must be greater than 0 or equal")
    logger.debug("func_test_send_sms_code_and_auth function is running")

    await func_test_send_sms_code(phone_number=phone_number)

    await sleep(sleep_time)

    redis_pool = Redis(host=redis_settings.REDIS_HOST, port=redis_settings.REDIS_PORT)

    sms_code_encoded: bytes = await redis_pool.get(phone_number)

    sms_code: str = sms_code_encoded.decode()

    await redis_pool.aclose()

    logger.info(f"sms_code = {sms_code}")

    await func_test_auth(phone_number=phone_number, sms_code=sms_code)


@pytest.mark.asyncio
async def test_send_sms_code_and_auth():
    logger.debug("test_send_sms_code_and_auth function is running")

    # logger.info("First user:")
    # access_token, refresh_token = await func_test_send_sms_code_and_auth(
    #     phone_number='+77053872095'
    # )
    #
    # logger.info(f"access_token: {access_token}")
    # logger.info(f"refresh_token: {refresh_token}")


    # logger.info("Second user:")
    # access_token, refresh_token = await func_test_send_sms_code_and_auth(
    #     phone_number='+77774691042',
    #     sleep_time=5
    # )
    #
    # logger.info(f"access_token: {access_token}")
    # logger.info(f"refresh_token: {refresh_token}")


    # logger.info("Third user:")
    # access_token, refresh_token = await func_test_send_sms_code_and_auth(
    #     phone_number='+79991709804',
    #     delay=timedelta(seconds=10)
    # )
    #
    # logger.info(f"access_token: {access_token}")
    # logger.info(f"refresh_token: {refresh_token}")


    # logger.info("Fourth user:")
    # access_token, refresh_token = await func_test_send_sms_code_and_auth(
    #     phone_number='+79276039852',
    #     delay=timedelta(minutes=2),
    #     sleep_time=10
    # )
    #
    # logger.info(f"access_token: {access_token}")
    # logger.info(f"refresh_token: {refresh_token}")


    logger.info("Fifth user:")
    await func_test_send_sms_code_and_auth(
        phone_number='+79228216018',
        # sleep_time=2
    )

    logger.info(f"client.cookies: {client.cookies.get("refresh_token")}")
    logger.info(f"client.headers: {client.headers}")

    await func_test_refresh()