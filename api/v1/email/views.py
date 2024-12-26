from starlette.responses import JSONResponse
from starlette import status
from fastapi import APIRouter, Depends
from redis.asyncio import Redis

from .schemas import EmailPasswordSchema
from database import AsyncSessionDep
from .utils import generate_email_code, get_redis_pool
from config import email_settings
from sqlmodel import select
from models import User
from exceptions import invalid_password_exception, invalid_email_exception, too_many_requests_exception
from api.v1.jwt.utils import validate_password
from tasks import send_email_verification_code

router = APIRouter()


@router.post("/auth")
async def send_verification_code(
        session: AsyncSessionDep,
        user_data: EmailPasswordSchema,
        redis_pool: Redis = Depends(get_redis_pool),
) -> JSONResponse:
    if await redis_pool.get(user_data.email):
        raise too_many_requests_exception

    statement = select(User).filter_by(email=user_data.email)
    try:
        result = await session.execute(statement)
    except:
        raise invalid_email_exception
    user = result.scalar()

    if user:
        if not validate_password(password=user_data.password, hashed_password=user.password):
            raise invalid_password_exception

    email_code = generate_email_code()

    send_email_verification_code(receiver_email=user_data.email, code=email_code)

    await redis_pool.set(user_data.email, email_code, ex=email_settings.expire_time)

    return JSONResponse(status_code=status.HTTP_200_OK, content={"message": "Код отправлен."})
