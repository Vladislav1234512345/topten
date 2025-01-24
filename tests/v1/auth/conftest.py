import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.testclient import TestClient

from src.database import async_engine, BaseModel, async_session_factory
from src.models import UserRole
from src.v1.auth import router
from src.v1.jwt.config import jwt_settings
from src.v1.jwt.utils import encode_jwt
import logging
from src.container import configure_logging
from src.config import logging_settings
from src.v1.sms.schemas import PhoneNumberPasswordSchema

logger = logging.getLogger(__name__)
configure_logging(level=logging_settings.logging_level)


@pytest.fixture(scope="module")
async def create_async_session() -> AsyncSession:
    async with async_session_factory() as session:
        yield session


async def delete_and_create_db_and_tables():

    async with async_engine.begin() as conn:
        await conn.run_sync(BaseModel.metadata.drop_all)
        logger.info("Dropped all tables from database.")
        await conn.run_sync(BaseModel.metadata.create_all)
        logger.info("Created all tables in database.")


class TestAuthUserSchema(PhoneNumberPasswordSchema):
    id: int
    role: UserRole


auth_user = TestAuthUserSchema(
    id=1,
    phone_number="antonkutorov@gmail.com",
    password="Qwerty1234",
    role=UserRole.user,
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
        "sub": auth_user.phone_number,
        "role": auth_user.role.value,
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
