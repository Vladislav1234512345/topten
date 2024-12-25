from starlette.responses import JSONResponse
from starlette import status
from fastapi import APIRouter, Depends
from redis.asyncio import Redis
from .validators import validate_phone_number

from .utils import generate_sms_code, get_redis_pool
from config import sms_settings

router = APIRouter()


@router.post("/send")
async def send_code(
        phone_number: str = Depends(validate_phone_number),
        redis_pool: Redis = Depends(get_redis_pool),

) -> JSONResponse:
    sms_code = generate_sms_code()
    await redis_pool.set(phone_number, sms_code, ex=sms_settings.expire_time)
    return JSONResponse(status_code=status.HTTP_200_OK, content={"message": "Код отправлен"})

