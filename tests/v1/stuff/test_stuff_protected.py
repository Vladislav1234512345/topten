import pytest

from src.v1.jwt.config import jwt_settings
from src.container import logger


@pytest.mark.asyncio
async def test_stuff_protected(client, create_access_token_stuff):
    access_token = await create_access_token_stuff
    authorization_header = f"{jwt_settings.access_token_type} {access_token}"
    client.headers["Authorization"] = authorization_header
    response = client.get("/stuff/protected")
    assert response.status_code == 200
    assert response.json()
    logger.info("/v1/stuff/protected was tested successfully.")
