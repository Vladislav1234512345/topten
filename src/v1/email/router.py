from starlette.responses import JSONResponse
from starlette import status
from fastapi import APIRouter, Depends
from redis.asyncio import Redis

from .schemas import EmailPasswordSchema, EmailSchema
from src.database import AsyncSessionDep, get_redis_pool
from .utils import generate_verification_code, generate_password
from .config import email_settings
from src.exceptions import (
    invalid_password_exception,
    user_not_found_exception,
    too_many_requests_exception,
)
from src.v1.jwt.utils import validate_password
from src.v1.email.tasks import send_email_reset_password, send_email_verification_code
from src.utils import select_user


router = APIRouter()


@router.post("/verification-code")
async def verification_code(
    session: AsyncSessionDep,
    user_data: EmailPasswordSchema,
    redis_pool: Redis = Depends(get_redis_pool),
) -> JSONResponse:
    verification_code_redis_key = (
        f"{email_settings.verification_code_name}:{user_data.email}"
    )
    if await redis_pool.get(verification_code_redis_key):
        raise too_many_requests_exception
    user = await select_user(session=session, email=user_data.email, get_password=True)

    if user:
        if not validate_password(
            password=user_data.password, hashed_password=user.password  # type: ignore
        ):
            raise invalid_password_exception
    email_code = generate_verification_code()
    send_email_verification_code.delay(
        receiver_email=str(user_data.email), code=email_code
    )
    await redis_pool.set(
        verification_code_redis_key, email_code, ex=email_settings.expire_time
    )

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"message": "Сообщение с кодом верификации успешно отправлено."},
    )


@router.post("/reset-password")
async def reset_password(
    session: AsyncSessionDep,
    user_data: EmailSchema,
    redis_pool: Redis = Depends(get_redis_pool),
) -> JSONResponse:
    reset_password_redis_key = f"{email_settings.reset_password_name}:{user_data.email}"
    if await redis_pool.get(reset_password_redis_key):
        raise too_many_requests_exception
    user = await select_user(session=session, email=user_data.email)

    if not user:
        raise user_not_found_exception
    email_reset_password_key = generate_password()
    send_email_reset_password.delay(
        receiver_email=str(user_data.email), key=email_reset_password_key
    )
    await redis_pool.set(
        reset_password_redis_key,
        email_reset_password_key,
        ex=email_settings.expire_time,
    )

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"message": "Сообщение для сброса пароля успешно отправлено."},
    )
