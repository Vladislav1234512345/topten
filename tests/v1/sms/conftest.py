import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.testclient import TestClient

from src.database import async_engine, BaseModel, async_session_factory
from src.models import UserModel, UserRole
from src.v1.users.utils import create_user
from src.v1.sms import router
from src.v1.auth.exceptions import current_user_yet_exists_exception
from src.v1.jwt.utils import hash_password
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


class TestSMSUserSchema(PhoneNumberPasswordSchema):
    id: int
    role: UserRole


sms_user = TestSMSUserSchema(
    id=1,
    phone_number="antonkutorov@gmail.com",
    password="Qwerty1234",
    role=UserRole.user,
)


@pytest.fixture(scope="module")
async def create_db_and_tables_and_user_phone_number() -> True:
    await delete_and_create_db_and_tables()
    async with async_session_factory() as session:
        user = await create_user(
            user=UserModel(
                phone_number=sms_user.phone_number,
                password=hash_password(password=sms_user.password),
                role=sms_user.role,
            ),
            session=session,
            exception=current_user_yet_exists_exception,
        )

    logger.info("User was created successfully!")

    return True


@pytest.fixture(scope="module")
async def get_sms_user() -> TestSMSUserSchema:
    return sms_user


@pytest.fixture(scope="module")
def client():
    return TestClient(router)
