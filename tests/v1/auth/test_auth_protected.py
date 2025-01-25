import pytest

from src.v1.jwt.config import jwt_settings
import logging
from src.container import configure_logging
from src.config import logging_settings

logger = logging.getLogger(__name__)
configure_logging(level=logging_settings.logging_level)


@pytest.mark.asyncio
async def test_auth_protected(client, create_access_token_auth):
    access_token = await create_access_token_auth
    authorization_header = f"{jwt_settings.access_token_type} {access_token}"
    client.headers["Authorization"] = authorization_header
    response = client.get("/auth/protected")
    logger.info(response.json())
    assert response.status_code == 200
    assert response.json()
    logger.info("/v1/auth/protected was tested successfully.")
