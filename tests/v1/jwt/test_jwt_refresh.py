import pytest

from src.container import logger
from src.v1.jwt.config import cookies_settings


@pytest.mark.asyncio
async def test_jwt_refresh(client, create_refresh_token_jwt):
    refresh_token = await create_refresh_token_jwt
    client.cookies.set(name=cookies_settings.refresh_token_name, value=refresh_token)
    response = client.post("/jwt/refresh")
    assert response.status_code == 200
    assert response.json() == {"message": "Токены успешно обновлены."}
    logger.info("/v1/auth/login was tested successfully.")
