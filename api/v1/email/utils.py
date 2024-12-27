from random import sample
from string import digits, ascii_letters
from redis.asyncio import from_url, Redis
from typing import AsyncIterator, LiteralString

from config import tasks_settings


def generate_password(symbols: LiteralString = digits + ascii_letters, length: int = 100) -> str:
    return ''.join(sample(symbols, length))


def generate_verification_code(symbols: LiteralString = digits, length: int = 6) -> str:
    return generate_password(symbols=symbols, length=length)


async def get_redis_pool() -> AsyncIterator[Redis]:
    redis: Redis = await from_url(
        f"redis://{tasks_settings.REDIS_HOST}:{tasks_settings.REDIS_PORT}",
        decode_responses=True
    )
    try:
        yield redis
    finally:
        await redis.aclose()
