import json

import pytest

from src.config import tasks_settings
import logging
from src.container import configure_logging
from src.config import logging_settings

from src.v1.email.config import email_settings
from src.v1.email.utils import generate_verification_code
from src.v1.auth.responses import login_response

from redis.asyncio import from_url


logger = logging.getLogger(__name__)
configure_logging(level=logging_settings.logging_level)


@pytest.mark.asyncio
async def test_auth_login(client, get_auth_user):
    user = await get_auth_user
    verification_code_redis_key = f"{email_settings.verification_code_key}:{user.email}"
    email_code = generate_verification_code()
    redis_pool = await from_url(  # type: ignore
        f"redis://{tasks_settings.REDIS_HOST}:{tasks_settings.REDIS_PORT}",
        decode_responses=True,
    )
    await redis_pool.set(
        verification_code_redis_key, email_code, ex=email_settings.expire_time
    )
    login_json_data = {
        "email_code": email_code,
        "email": user.email,
        "password": user.password,
    }
    response = client.post("/auth/login", content=json.dumps(login_json_data))
    redis_pool.aclose()
    assert response.status_code == login_response.status_code
    assert response.json() == json.loads(login_response.body)
    logger.info("/v1/auth/login was tested successfully.")
