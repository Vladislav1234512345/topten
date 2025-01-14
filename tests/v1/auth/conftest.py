import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.testclient import TestClient

from src.database import async_engine, Base, async_session_factory
from src.models import UserModel
from src.utils import create_user
from src.v1.auth import router
from src.v1.auth.exceptions import current_user_yet_exists_exception
from src.v1.email.schemas import EmailPasswordSchema
from src.v1.jwt.config import jwt_settings
from src.v1.jwt.utils import hash_password, encode_jwt
from src.container import logger


@pytest.fixture(scope="module")
async def create_async_session() -> AsyncSession:
    async with async_session_factory() as session:
        yield session


async def delete_and_create_db_and_tables():

    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        logger.info("Dropped all tables from database...")
        await conn.run_sync(Base.metadata.create_all)
        logger.info("Created all tables in database...")


class TestAuthUserSchema(EmailPasswordSchema):
    id: int
    first_name: str
    is_admin: bool
    is_stuff: bool


auth_user = TestAuthUserSchema(
    id=1,
    email="antonkutorov@gmail.com",
    password="qwerty1234",
    first_name="Vladislav",
    is_admin=False,
    is_stuff=False,
)


@pytest.fixture(scope="module")
async def create_db_and_tables_and_user_auth() -> True:
    await delete_and_create_db_and_tables()

    return True


@pytest.fixture(scope="module")
async def create_access_token_auth() -> str:
    jwt_payload_access_token = {
        "type": jwt_settings.jwt_access_token_type,
        "uid": auth_user.id,
        "sub": auth_user.email,
        "name": auth_user.first_name,
        "admin": auth_user.is_admin,
        "stuff": auth_user.is_stuff,
    }

    access_token = encode_jwt(
        payload=jwt_payload_access_token,
        expire_timedelta=jwt_settings.access_token_expire_minutes,
    )

    return access_token


@pytest.fixture(scope="module")
async def get_auth_user() -> TestAuthUserSchema:
    return auth_user


@pytest.fixture(scope="module")
def client():
    return TestClient(router)
