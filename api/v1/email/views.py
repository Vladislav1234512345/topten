from starlette.responses import JSONResponse
from starlette import status
from fastapi import APIRouter, Depends, HTTPException
from redis.asyncio import Redis

from .schemas import UserSendEmailSchema
from database import AsyncSessionDep
from .utils import generate_email_code, get_redis_pool
from config import email_settings
from sqlmodel import select
from models import User
from api.v1.jwt.exceptions import unauthorized_exception
from api.v1.jwt.utils import validate_password

router = APIRouter()


@router.post("/send")
async def send_code(
        session: AsyncSessionDep,
        user_data: UserSendEmailSchema,
        redis_pool: Redis = Depends(get_redis_pool),
) -> JSONResponse:
    if await redis_pool.get(user_data.email):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Слишком частые запросы. Попробуйте позже."
        )

    statement = select(User).filter_by(email=user_data.email)
    try:
        result = await session.execute(statement)
    except:
        raise unauthorized_exception
    user = result.scalar()

    if user:
        if not validate_password(password=user_data.password, hashed_password=user.password):
            raise unauthorized_exception

    email_code = generate_email_code()

    await redis_pool.set(user_data.email, email_code, ex=email_settings.expire_time)

    return JSONResponse(status_code=status.HTTP_200_OK, content={"message": "Код отправлен"})
