import json

import pytest

import logging
from src.container import configure_logging
from src.config import logging_settings
from src.v1.email.responses import reset_password_email_response

logger = logging.getLogger(__name__)
configure_logging(level=logging_settings.logging_level)


@pytest.mark.asyncio
async def test_email_reset_password(client, get_email_user):
    user = await get_email_user
    reset_password_json_data = {"email": user.email}
    response = client.post(
        "/email/reset-password", content=json.dumps(reset_password_json_data)
    )
    assert response.status_code == reset_password_email_response.status_code
    assert response.json() == json.loads(reset_password_email_response.body)
    logger.info("/v1/email/reset-password was tested.")
