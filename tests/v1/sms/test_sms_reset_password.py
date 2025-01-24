import json

import pytest

import logging
from src.container import configure_logging
from src.config import logging_settings
from src.v1.sms.responses import reset_password_sms_response

logger = logging.getLogger(__name__)
configure_logging(level=logging_settings.logging_level)


@pytest.mark.asyncio
async def test_sms_reset_password(client, get_sms_user):
    user = await get_sms_user
    reset_password_json_data = {"phone_number": user.phone_number}
    response = client.post(
        "/sms/reset-password", content=json.dumps(reset_password_json_data)
    )
    assert response.status_code == reset_password_sms_response.status_code
    assert response.json() == json.loads(reset_password_sms_response.body)
    logger.info("/v1/sms/reset-password was tested.")
