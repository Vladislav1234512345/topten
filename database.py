from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlmodel import SQLModel, select, Session
from typing import AsyncGenerator, Annotated

from config import database_settings

postgresql_url = (
    f"postgresql+asyncpg://"
    f"{database_settings.POSTGRES_USER}:{database_settings.POSTGRES_PASSWORD}"
    f"@{database_settings.POSTGRES_HOST}:{database_settings.POSTGRES_PORT}"
    f"/{database_settings.POSTGRES_DB}"
)

engine = create_async_engine(postgresql_url)


async def create_db_and_tables():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSession(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]
