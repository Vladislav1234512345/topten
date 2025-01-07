from fastapi.testclient import TestClient
from pydantic import BaseModel

from src.v1.admin import router
from src.v1.jwt.config import jwt_settings
from src.v1.jwt.utils import encode_jwt
from src.container import logger
import datetime
from src.schemas import UserSchema

client = TestClient(router)


def create_access_token_mock(user: UserSchema) -> str:
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


def test_is_user_admin():
    now = datetime.datetime.now()
    access_token = create_access_token_mock(user=UserSchema(id=1, email="antonkutorov@gmail.com", first_name="Vladislav", is_admin=True, is_stuff=True, is_active=True, created_at=now, updated_at=now))
    authorization_header = f"{jwt_settings.access_token_type} {access_token}"
    logger.info(f"authorization_header = {authorization_header}")
    client.headers['Authorization'] = authorization_header
    response = client.get('/admin/protected')
    assert response.status_code == 200
    logger.info(f"{response.json()=}")
    assert response.json()