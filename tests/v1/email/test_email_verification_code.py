import json

import pytest

import logging
from src.container import configure_logging
from src.config import logging_settings
from src.v1.email.responses import verification_code_email_response

logger = logging.getLogger(__name__)
configure_logging(level=logging_settings.logging_level)


@pytest.mark.asyncio
async def test_email_verification_code(client, get_email_user):
    user = await get_email_user
    verification_code_json_data = {
        "email": user.email,
        "password": user.password,
    }
    response = client.post(
        "/email/verification-code", content=json.dumps(verification_code_json_data)
    )
    assert response.status_code == verification_code_email_response.status_code
    assert response.json() == json.loads(verification_code_email_response.body)
    logger.info("/v1/email/verification-code was tested successfully.")
