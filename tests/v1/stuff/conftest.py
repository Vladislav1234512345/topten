import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.testclient import TestClient

from src.database import async_engine, BaseModel, AsyncSessionDep, async_session_factory
from src.models import UserModel, UserRole
from src.utils import create_user
from src.v1.sms.schemas import PhoneNumberPasswordSchema
from src.v1.stuff import router
from src.exceptions import current_user_yet_exists_exception
from src.v1.jwt.config import jwt_settings
from src.v1.jwt.utils import encode_jwt, hash_password
import logging
from src.container import configure_logging
from src.config import logging_settings

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


class TestStuffUserSchema(PhoneNumberPasswordSchema):
    id: int
    role: UserRole


stuff_user = TestStuffUserSchema(
    id=1,
    phone_number="antonkutorov@gmail.com",
    password="Qwerty1234",
    role=UserRole.stuff,
)


@pytest.fixture(scope="module")
async def create_db_and_tables_and_user_stuff() -> True:
    await delete_and_create_db_and_tables()
    async with async_session_factory() as session:
        user = await create_user(
            user=UserModel(
                phone_number=stuff_user.phone_number,
                password=hash_password(password=stuff_user.password),
                role=stuff_user.role,
            ),
            session=session,
            exception=current_user_yet_exists_exception,
        )

    logger.info("User was created successfully!")

    return True


@pytest.fixture(scope="module")
async def create_access_token_stuff() -> str:
    jwt_payload_access_token = {
        "type": jwt_settings.jwt_access_token_type,
        "uid": stuff_user.id,
        "sub": stuff_user.phone_number,
        "role": stuff_user.role.value,
    }
    access_token = encode_jwt(
        payload=jwt_payload_access_token,
        expire_timedelta=jwt_settings.access_token_expire_minutes,
    )

    return access_token


@pytest.fixture(scope="module")
def client():
    return TestClient(router)
