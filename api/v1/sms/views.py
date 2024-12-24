from starlette import status
from starlette.responses import JSONResponse

from fastapi import APIRouter, Depends
from .validators import validate_phone_number

from .utils import generate_sms_code, get_redis_pool

router = APIRouter()


@router.post("/send")
async def send_code(
        phone_number: str = Depends(validate_phone_number),
        redis_pool=Depends(get_redis_pool)
) -> JSONResponse:
    sms_code = generate_sms_code()
    await redis_pool.set(phone_number, sms_code, expire=300)
    return JSONResponse(status_code=status.HTTP_200_OK, content={"message": "Код отправлен"})

