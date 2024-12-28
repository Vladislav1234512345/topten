from random import choice
from string import digits, ascii_letters
from redis.asyncio import from_url, Redis
from typing import AsyncIterator, LiteralString

from config import tasks_settings


def generate_password(
    population: str = digits + ascii_letters, length: int = 100
) -> str:
    password = ""
    for _ in range(length):
        password += choice(population)

    return password



def generate_verification_code(symbols: LiteralString = digits, length: int = 6) -> str:
    return generate_password(population=symbols, length=length)


async def get_redis_pool() -> AsyncIterator[Redis]:
    redis: Redis = await from_url(
        f"redis://{tasks_settings.REDIS_HOST}:{tasks_settings.REDIS_PORT}",
        decode_responses=True
    )
    try:
        yield redis
    finally:
        await redis.aclose()
