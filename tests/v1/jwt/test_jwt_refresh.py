import json

import pytest

from src.v1.jwt.config import cookies_settings
import logging
from src.container import configure_logging
from src.config import logging_settings
from src.v1.jwt.responses import tokens_refresh_response

logger = logging.getLogger(__name__)
configure_logging(level=logging_settings.logging_level)


@pytest.mark.asyncio
async def test_jwt_refresh(client, create_refresh_token_jwt):
    refresh_token = await create_refresh_token_jwt
    client.cookies.set(name=cookies_settings.refresh_token_name, value=refresh_token)
    response = client.post("/jwt/refresh")
    assert response.status_code == tokens_refresh_response.status_code
    assert response.json() == json.loads(tokens_refresh_response.body)
    logger.info("/v1/auth/login was tested successfully.")
