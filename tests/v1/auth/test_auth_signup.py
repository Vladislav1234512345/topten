import json

import pytest

from src.config import tasks_settings
import logging
from src.container import configure_logging
from src.config import logging_settings
from src.v1.auth.responses import signup_response

from src.v1.sms.config import sms_settings
from src.v1.sms.utils import generate_verification_code

from redis.asyncio import from_url

logger = logging.getLogger(__name__)
configure_logging(level=logging_settings.logging_level)


@pytest.mark.asyncio
async def test_auth_signup(client, get_auth_user):
    user = await get_auth_user
    verification_code_redis_key = (
        f"{sms_settings.verification_code_key}:{user.phone_number}"
    )
    sms_code = generate_verification_code()
    redis_pool = await from_url(  # type: ignore
        f"redis://{tasks_settings.REDIS_HOST}:{tasks_settings.REDIS_PORT}",
        decode_responses=True,
    )
    await redis_pool.set(
        verification_code_redis_key, sms_code, ex=sms_settings.expire_time
    )
    signup_json_data = {
        "sms_code": sms_code,
        "phone_number": user.phone_number,
        "password": user.password,
        "first_name": user.first_name,
    }
    response = client.post("/auth/signup", content=json.dumps(signup_json_data))
    redis_pool.aclose()
    assert response.status_code == signup_response.status_code
    assert response.json() == json.loads(signup_response.body)
    logger.info("/v1/auth/signup was tested successfully.")
