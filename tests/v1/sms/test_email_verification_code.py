import json

import pytest

import logging
from src.container import configure_logging
from src.config import logging_settings
from src.v1.sms.responses import verification_code_sms_response

logger = logging.getLogger(__name__)
configure_logging(level=logging_settings.logging_level)


@pytest.mark.asyncio
async def test_sms_verification_code(client, get_sms_user):
    user = await get_sms_user
    verification_code_json_data = {
        "phone_number": user.phone_number,
        "password": user.password,
    }
    response = client.post(
        "/sms/verification-code", content=json.dumps(verification_code_json_data)
    )
    assert response.status_code == verification_code_sms_response.status_code
    assert response.json() == json.loads(verification_code_sms_response.body)
    logger.info("/v1/sms/verification-code was tested successfully.")
