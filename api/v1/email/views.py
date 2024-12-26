from starlette.responses import JSONResponse
from starlette import status
from fastapi import APIRouter, Depends, HTTPException
from redis.asyncio import Redis

from .schemas import EmailSchema
from .utils import generate_email_code, get_redis_pool
from config import email_settings


router = APIRouter()


@router.post("/send")
async def send_code(
        email_schema: EmailSchema,
        redis_pool: Redis = Depends(get_redis_pool),
) -> JSONResponse:
    if await redis_pool.get(email_schema.email):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Слишком частые запросы. Попробуйте позже."
        )
    email_code = generate_email_code()
    print(email_code)

    await redis_pool.set(email_schema.email, email_code, ex=email_settings.expire_time)
    return JSONResponse(status_code=status.HTTP_200_OK, content={"message": "Код отправлен"})
