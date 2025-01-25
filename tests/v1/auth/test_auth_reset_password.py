import json

import pytest

from src.config import tasks_settings
import logging
from src.container import configure_logging
from src.config import logging_settings

from src.v1.sms.config import sms_settings
from src.v1.sms.utils import generate_password
from src.v1.auth.responses import reset_password_response

from redis.asyncio import from_url


logger = logging.getLogger(__name__)
configure_logging(level=logging_settings.logging_level)


@pytest.mark.asyncio
async def test_auth_reset_password(client, get_auth_user):
    user = await get_auth_user
    sms_reset_password = generate_password()
    reset_password_redis_key = f"{sms_settings.reset_password_key}:{sms_reset_password}"
    redis_pool = await from_url(
        f"redis://:{tasks_settings.REDIS_PASSWORD}@{tasks_settings.REDIS_HOST}:{tasks_settings.REDIS_PORT}",
        decode_responses=True,
    )
    await redis_pool.set(
        reset_password_redis_key, user.phone_number, ex=sms_settings.expire_time
    )
    redis_pool.aclose()
    reset_password_json_data = {
        "password": user.password,
        "password_reset": user.password,
    }
    logger.info(reset_password_json_data)
    response = client.post(
        f"/auth/reset-password/{sms_reset_password}",
        content=json.dumps(reset_password_json_data),
    )
    logger.info(response.json())
    assert response.status_code == reset_password_response.status_code
    assert response.json() == json.loads(reset_password_response.body)
    logger.info("/v1/auth/reset-password was tested successfully.")
