import json

import pytest

from src.container import logger


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
    assert response.status_code == 200
    assert response.json() == {
        "message": "Сообщение с кодом верификации успешно отправлено."
    }
    logger.info("/v1/email/verification-code was tested successfully.")
