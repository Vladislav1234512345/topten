import json

import pytest

import logging
from src.container import configure_logging
from src.config import logging_settings
from src.v1.jwt.responses import tokens_refresh_response
from starlette import status

logger = logging.getLogger(__name__)
configure_logging(level=logging_settings.logging_level)


@pytest.mark.asyncio
async def test_jwt_refresh(client, create_access_token_jwt):
    access_token = await create_access_token_jwt
    client.headers.update({"Authorization": access_token})
    response = client.get("/profile/me")
    logger.info(response.json())
    assert response.status_code == status.HTTP_200_OK
    assert response.json()
    logger.info("/v1/profile/me was tested successfully.")
