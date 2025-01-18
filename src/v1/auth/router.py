from fastapi import APIRouter, Depends
from redis.asyncio import Redis
from starlette.responses import JSONResponse

from src.utils import select_user, update_user_with_email
from src.v1.jwt.dependencies import get_current_user_with_access_token
from src.v1.jwt.utils import hash_password, set_tokens_in_response, validate_password
from src.v1.email.config import email_settings
from src.database import AsyncSessionDep, get_redis_pool
from src.utils import create_user
from src.schemas import UserSchema
from src.models import UserModel
from src.v1.email.schemas import (
    EmailPasswordFirstNameVerificationCodeSchema,
    EmailPasswordVerificationCodeSchema,
    EmailTwoPasswordsSchema,
)
from src.exceptions import (
    invalid_email_code_exception,
    user_not_found_exception,
    invalid_password_exception,
)
from src.v1.auth.exceptions import (
    invalid_reset_password_key_exception,
    current_user_yet_exists_exception,
)
from .responses import reset_password_response, signup_response, login_response
import logging
from src.container import configure_logging
from src.config import logging_settings

logger = logging.getLogger(__name__)
configure_logging(level=logging_settings.logging_level)


router = APIRouter()


@router.post("/signup")
async def signup(
    session: AsyncSessionDep,
    user_data: EmailPasswordFirstNameVerificationCodeSchema,
    redis_pool: Redis = Depends(get_redis_pool),
) -> JSONResponse:
    verification_code_redis_key = (
        f"{email_settings.verification_code_name}:{user_data.email}"
    )
    stored_code: str = await redis_pool.get(verification_code_redis_key)
    if stored_code != user_data.email_code:
        logger.warning(
            "Incorrect verification code, email: %s, expected code: %s, received code: %s",
            user_data.email_code,
            stored_code,
            user_data.email_code,
        )
        raise invalid_email_code_exception
    user = await create_user(
        user=UserModel(
            email=user_data.email,
            password=hash_password(password=user_data.password),
            first_name=user_data.first_name,
        ),
        session=session,
        exception=current_user_yet_exists_exception,
    )
    await redis_pool.delete(verification_code_redis_key)

    logger.info(f"User have successfully signed up, email: %s", user_data.email)
    return set_tokens_in_response(response=signup_response, user=user)


@router.post("/login")
async def login(
    session: AsyncSessionDep,
    user_data: EmailPasswordVerificationCodeSchema,
    redis_pool: Redis = Depends(get_redis_pool),
) -> JSONResponse:
    verification_code_redis_key = (
        f"{email_settings.verification_code_name}:{user_data.email}"
    )
    user = await select_user(session=session, get_password=True, email=user_data.email)

    if not user:
        logger.warning("User not found, email: %s", user_data.email)
        raise user_not_found_exception
    if not validate_password(
        password=user_data.password, hashed_password=user.password  # type: ignore
    ):
        logger.warning("Incorrect password, email: %s", user_data.email)
        raise invalid_password_exception
    stored_code: str = await redis_pool.get(verification_code_redis_key)
    if stored_code != user_data.email_code:
        logger.warning(
            "Incorrect verification code, email: %s, expected code: %s, received code: %s",
            user_data.email,
            stored_code,
            user_data.email_code,
        )
        raise invalid_email_code_exception
    await redis_pool.delete(verification_code_redis_key)

    logger.info(f"User have successfully logged in, email: %s", user_data.email)
    return set_tokens_in_response(response=login_response, user=user)


@router.post("/reset-password/{key}")
async def reset_password(
    key: str,
    session: AsyncSessionDep,
    user_data: EmailTwoPasswordsSchema,
    redis_pool: Redis = Depends(get_redis_pool),
) -> JSONResponse:
    reset_password_redis_key = f"{email_settings.reset_password_name}:{user_data.email}"
    stored_reset_password_key: str = await redis_pool.get(reset_password_redis_key)
    if key != stored_reset_password_key:
        logger.warning("Incorrect reset password key, email: %s", user_data.email)
        raise invalid_reset_password_key_exception

    await update_user_with_email(
        session=session,
        user_email=user_data.email,
        show_user=False,
        password=hash_password(password=user_data.password),
    )

    await redis_pool.delete(reset_password_redis_key)
    logger.info(
        f"User have successfully updated the password, email: %s", user_data.email
    )
    return reset_password_response


@router.get("/protected", response_model=UserSchema)
async def protected(
    user: UserSchema = Depends(get_current_user_with_access_token),
) -> UserSchema:
    logger.info(
        f"User have successfully visited the protected page, email: %s", user.email
    )

    return user
