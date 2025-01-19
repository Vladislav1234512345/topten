from starlette.responses import JSONResponse
from fastapi import APIRouter, Depends
from redis.asyncio import Redis

from .schemas import EmailPasswordSchema, EmailSchema
from .responses import verification_code_email_response, reset_password_email_response
from src.database import AsyncSessionDep, get_redis_pool
from .utils import generate_verification_code, generate_password
from .config import email_settings
from src.exceptions import (
    invalid_password_exception,
    user_not_found_exception,
    too_many_email_requests_exception,
)
from src.v1.jwt.utils import validate_password
from src.v1.email.tasks import send_email_reset_password, send_email_verification_code
from src.utils import select_user
import logging
from src.container import configure_logging
from src.config import logging_settings
from ..auth.exceptions import current_user_yet_exists_exception

logger = logging.getLogger(__name__)
configure_logging(level=logging_settings.logging_level)


router = APIRouter()


@router.post("/verification-code")
async def verification_code(
    session: AsyncSessionDep,
    user_data: EmailPasswordSchema,
    redis_pool: Redis = Depends(get_redis_pool),
    is_new_account: bool = False,
) -> JSONResponse:
    verification_code_redis_key = (
        f"{email_settings.verification_code_name}:{user_data.email}"
    )
    if await redis_pool.get(verification_code_redis_key):
        logger.warning(
            "Too many requests ('/v1/email/verification-code'), email: %s",
            user_data.email,
        )
        raise too_many_email_requests_exception
    user = await select_user(session=session, email=user_data.email, get_password=True)

    if user:
        if is_new_account:
            logger.warning("Current user has been existed yet, email: %s", user.email)
            raise current_user_yet_exists_exception
        if not validate_password(
            password=user_data.password, hashed_password=user.password  # type: ignore
        ):
            logger.warning("Incorrect password, email: %s", user_data.email)
            raise invalid_password_exception
    else:
        if not is_new_account:
            raise user_not_found_exception

    email_code = generate_verification_code()
    send_email_verification_code.delay(
        receiver_email=str(user_data.email), code=email_code
    )
    await redis_pool.set(
        verification_code_redis_key, email_code, ex=email_settings.expire_time
    )
    logger.info(
        "The verification code email has been successfully sent to user, email: %s",
        user_data.email,
    )
    return verification_code_email_response


@router.post("/reset-password")
async def reset_password(
    session: AsyncSessionDep,
    user_data: EmailSchema,
    redis_pool: Redis = Depends(get_redis_pool),
) -> JSONResponse:
    reset_password_redis_key = f"{email_settings.reset_password_name}:{user_data.email}"
    if await redis_pool.get(reset_password_redis_key):
        logger.warning(
            "Too many requests ('/v1/email/reset-password'), email: %s", user_data.email
        )
        raise too_many_email_requests_exception
    user = await select_user(session=session, email=user_data.email)

    if not user:
        logger.warning("Incorrect password, email: %s", user_data.email)
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
    logger.info(
        "The password reset email has been successfully sent to the user, email: %s",
        user_data.email,
    )
    return reset_password_email_response
