import json

import pytest

from src.container import logger


@pytest.mark.asyncio
async def test_email_reset_password(client, get_email_user):
    user = await get_email_user
    reset_password_json_data = {"email": user.email}
    response = client.post(
        "/email/reset-password", content=json.dumps(reset_password_json_data)
    )
    assert response.status_code == 200
    assert response.json() == {
        "message": "Сообщение для сброса пароля успешно отправлено."
    }
    logger.info("/v1/email/reset-password was tested ...")
