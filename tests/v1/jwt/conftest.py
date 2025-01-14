import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.testclient import TestClient

from src.database import async_engine, Base, AsyncSessionDep, async_session_factory
from src.models import UserModel
from src.utils import create_user
from src.v1.jwt import router
from src.v1.auth.exceptions import current_user_yet_exists_exception
from src.v1.email.schemas import EmailPasswordSchema
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
        await conn.run_sync(Base.metadata.drop_all)
        logger.info("Dropped all tables from database...")
        await conn.run_sync(Base.metadata.create_all)
        logger.info("Created all tables in database...")


class TestJwtUserSchema(EmailPasswordSchema):
    id: int
    first_name: str
    is_admin: bool
    is_stuff: bool


jwt_user = TestJwtUserSchema(
    id=1,
    email="antonkutorov@gmail.com",
    password="qwerty1234",
    first_name="Vladislav",
    is_admin=False,
    is_stuff=True,
)


@pytest.fixture(scope="module")
async def create_db_and_tables_and_user_jwt() -> True:
    await delete_and_create_db_and_tables()
    async with async_session_factory() as session:
        user = await create_user(
            user=UserModel(
                email=jwt_user.email,
                password=hash_password(password=jwt_user.password),
                first_name=jwt_user.first_name,
                is_admin=jwt_user.is_admin,
                is_stuff=jwt_user.is_stuff,
            ),
            session=session,
            exception=current_user_yet_exists_exception,
        )

    logger.info("User was created successfully!")

    return True


@pytest.fixture(scope="module")
async def create_refresh_token_jwt() -> str:
    jwt_payload_refresh_token = {
        "type": jwt_settings.jwt_refresh_token_type,
        "uid": jwt_user.id,
        "sub": jwt_user.email,
        "name": jwt_user.first_name,
        "admin": jwt_user.is_admin,
        "stuff": jwt_user.is_stuff,
    }
    refresh_token = encode_jwt(
        payload=jwt_payload_refresh_token,
        expire_timedelta=jwt_settings.access_token_expire_minutes,
    )

    return refresh_token


@pytest.fixture(scope="module")
def client():
    return TestClient(router)
