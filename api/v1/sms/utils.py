from random import sample
from string import digits
from redis.asyncio import from_url, Redis
from typing import AsyncIterator

from config import redis_settings


def generate_sms_code(length: int = 6):
    return ''.join(sample(digits, length))


async def get_redis_pool() -> AsyncIterator[Redis]:
    redis = await from_url(
        f"redis://{redis_settings.REDIS_HOST}:{redis_settings.REDIS_PORT}",
        decode_responses=True
    )
    try:
        yield redis
    finally:
        await redis.aclose()
