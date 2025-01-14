from typing import Annotated, AsyncGenerator, AsyncIterator

from fastapi import Depends
from redis.asyncio import Redis, from_url
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, mapped_column
from sqlalchemy import text, String
import datetime
import logging

from src.config import database_settings, tasks_settings, logging_settings
from src.container import configure_logging


logger = logging.getLogger(__name__)
configure_logging(level=logging_settings.logging_level)


intpk = Annotated[int, mapped_column(primary_key=True)]
str_256 = Annotated[str, 256]
created_at = Annotated[
    datetime.datetime, mapped_column(server_default=text("TIMEZONE('UTC', now())"))
]
updated_at = Annotated[
    datetime.datetime,
    mapped_column(
        server_default=text("TIMEZONE('UTC', now())"), onupdate=datetime.datetime.utcnow
    ),
]


class Base(DeclarativeBase):
    type_annotation_map = {str_256: String(length=256)}

    columns_count = 4
    extra_column = ()

    def __repr__(self) -> str:
        columns = []
        for id, column in enumerate(self.__table__.columns.keys()):
            if id < self.columns_count or column in self.extra_column:
                columns.append(f"{column}={getattr(self, column)}")

        return f"{self.__class__.__name__}({', '.join(columns)})"


async_engine = create_async_engine(
    url=database_settings.POSTGRES_URL_asyncpg, echo=False
)


async_session_factory = async_sessionmaker(
    bind=async_engine, class_=AsyncSession, expire_on_commit=False
)


async def create_db_and_tables() -> None:
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        logger.info("Создал все метаданные в базе данных!")


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_factory() as async_session:
        yield async_session


AsyncSessionDep = Annotated[AsyncSession, Depends(get_async_session)]


async def get_redis_pool() -> AsyncIterator[Redis]:
    redis = await from_url(  # type: ignore
        f"redis://{tasks_settings.REDIS_HOST}:{tasks_settings.REDIS_PORT}",
        decode_responses=True,
    )
    try:
        yield redis
    finally:
        await redis.aclose()
