from fastapi.testclient import TestClient
from pydantic import BaseModel

from src.v1.stuff import router
from src.v1.jwt.config import jwt_settings
from src.v1.jwt.utils import encode_jwt
from src.container import logger

client = TestClient(router)


class UserMock(BaseModel):
    id: int = 1
    email: str = "antonkutorov@gmail.com"
    first_name: str = "Vladislav"
    is_admin: bool = False
    is_stuff: bool = True


def create_access_token_mock(user: UserMock) -> str:
    jwt_payload_access_token = {
        "type": jwt_settings.jwt_access_token_type,
        "uid": user.id,
        "sub": user.email,
        "name": user.first_name,
        "admin": user.is_admin,
        "stuff": user.is_stuff,
    }

    access_token = encode_jwt(
        payload=jwt_payload_access_token,
        expire_timedelta=jwt_settings.access_token_expire_minutes,
    )

    return access_token


def test_is_user_stuff() -> None:
    user = UserMock()
    access_token = create_access_token_mock(user=user)
    authorization_header = f"{jwt_settings.access_token_type} {access_token}"
    logger.info(f"authorization_header = {authorization_header}")
    client.headers['Authorization'] = authorization_header
    response = client.get('/stuff/protected')
    assert response.status_code == 200
    logger.info(f"{response.json()=}")
    assert response.json()