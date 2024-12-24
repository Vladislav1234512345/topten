from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel

from config import database_settings


postgresql_url = (
    f"postgresql+asyncpg://"
    f"{database_settings.POSTGRES_USER}:{database_settings.POSTGRES_PASSWORD}"
    f"@{database_settings.POSTGRES_HOST}:{database_settings.POSTGRES_PORT}"
    f"/{database_settings.POSTGRES_DB}"
)

engine = create_async_engine(url=postgresql_url, echo=True)


async_session = sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)


engine = create_async_engine(postgresql_url)


async def create_db_and_tables():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session


AsyncSessionDep = Annotated[AsyncSession, Depends(get_session)]
