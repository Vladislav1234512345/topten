from fastapi import APIRouter, Depends
from redis.asyncio import Redis
from starlette.responses import JSONResponse

from src.v1.jwt.dependencies import get_current_user_with_access_token
from src.v1.jwt.utils import set_tokens_in_response
from src.database import AsyncSessionDep, get_redis_pool
from src.utils import create_user, select_user
from src.schemas import UserSchema
from src.models import UserModel
from src.exceptions import (
    invalid_sms_code_exception,
    current_user_yet_exists_exception,
)
from .responses import auth_response
import logging
from src.container import configure_logging
from src.config import logging_settings
from src.v1.sms.config import sms_settings
from src.v1.sms.schemas import (
    PhoneNumberVerificationCodeSchema,
)

logger = logging.getLogger(__name__)
configure_logging(level=logging_settings.logging_level)


router = APIRouter()


@router.post("/")
async def auth_view(
    session: AsyncSessionDep,
    user_auth_data: PhoneNumberVerificationCodeSchema,
    redis_pool: Redis = Depends(get_redis_pool),
) -> JSONResponse:
    verification_code_redis_key = (
        f"{sms_settings.verification_code_key}:{user_auth_data.phone_number}"
    )
    stored_code = await redis_pool.get(verification_code_redis_key)
    if stored_code != user_auth_data.sms_code:
        logger.warning(
            "Incorrect verification code, phone number: %s, expected code: %s, received code: %s",
            user_auth_data.phone_number,
            stored_code,
            user_auth_data.sms_code,
        )
        raise invalid_sms_code_exception

    user = await select_user(
        session=session,
        full_info=False,
        exclude_none=False,
        phone_number=user_auth_data.phone_number,
    )

    if user is None:
        user = await create_user(
            user=UserModel(
                phone_number=user_auth_data.phone_number,
            ),
            session=session,
            exception=current_user_yet_exists_exception,
        )
    await redis_pool.delete(verification_code_redis_key)

    logger.info(
        f"User has been successfully authorized, phone number: %s",
        user_auth_data.phone_number,
    )
    return set_tokens_in_response(response=auth_response, user=user)


# @router.post("/signup")
# async def signup_view(
#     session: AsyncSessionDep,
#     user_data: PhoneNumberPasswordFirstNameVerificationCodeSchema,
#     redis_pool: Redis = Depends(get_redis_pool),
# ) -> JSONResponse:
#     verification_code_redis_key = (
#         f"{sms_settings.verification_code_key}:{user_data.phone_number}"
#     )
#     stored_code = await redis_pool.get(verification_code_redis_key)
#     if stored_code != user_data.sms_code:
#         logger.warning(
#             "Incorrect verification code, phone number: %s, expected code: %s, received code: %s",
#             user_data.phone_number,
#             stored_code,
#             user_data.sms_code,
#         )
#         raise invalid_sms_code_exception
#     user = await create_user(
#         user=UserModel(
#             phone_number=user_data.phone_number,
#             password=hash_password(password=user_data.password),
#         ),
#         session=session,
#         exception=current_user_yet_exists_exception,
#     )
#     await redis_pool.delete(verification_code_redis_key)
#
#     logger.info(
#         f"User have successfully signed up, phone number: %s", user_data.phone_number
#     )
#     return set_tokens_in_response(response=signup_response, user=user)
#
#
# @router.post("/login")
# async def login_view(
#     session: AsyncSessionDep,
#     user_data: PhoneNumberPasswordVerificationCodeSchema,
#     redis_pool: Redis = Depends(get_redis_pool),
# ) -> JSONResponse:
#     verification_code_redis_key = (
#         f"{sms_settings.verification_code_key}:{user_data.phone_number}"
#     )
#     user = await select_user(
#         session=session,
#         full_info=False,
#         get_password=True,
#         phone_number=user_data.phone_number,
#     )
#
#     if not user:
#         logger.warning("User not found, phone number: %s", user_data.phone_number)
#         raise user_not_found_exception
#     if not validate_password(
#         password=user_data.password, hashed_password=user.password  # type: ignore
#     ):
#         logger.warning("Incorrect password, phone number: %s", user_data.phone_number)
#         raise invalid_password_exception
#     stored_code = await redis_pool.get(verification_code_redis_key)
#     if stored_code != user_data.sms_code:
#         logger.warning(
#             "Incorrect verification code, phone number: %s, expected code: %s, received code: %s",
#             user_data.phone_number,
#             stored_code,
#             user_data.sms_code,
#         )
#         raise invalid_sms_code_exception
#     await redis_pool.delete(verification_code_redis_key)
#
#     logger.info(
#         f"User have successfully logged in, phone number: %s", user_data.phone_number
#     )
#     return set_tokens_in_response(response=login_response, user=user)
#
#
# @router.post("/reset-password/{key}")
# async def reset_password_view(
#     key: str,
#     session: AsyncSessionDep,
#     user_data: TwoPasswordsSchema,
#     redis_pool: Redis = Depends(get_redis_pool),
# ) -> JSONResponse:
#     reset_password_redis_key = f"{sms_settings.reset_password_key}:{key}"
#     user_phone_number_from_redis_pool = await redis_pool.get(reset_password_redis_key)
#     if user_phone_number_from_redis_pool is None:
#         logger.warning("Incorrect reset password key.")
#         raise invalid_reset_password_key_exception
#     await update_user_with_phone_number(
#         session=session,
#         user_phone_number=user_phone_number_from_redis_pool,
#         show_user=False,
#         password=hash_password(password=user_data.password),
#     )
#
#     await redis_pool.delete(reset_password_redis_key)
#     logger.info(
#         f"User have successfully updated the password, phone number: %s",
#         user_phone_number_from_redis_pool,
#     )
#     return reset_password_response


@router.get("/protected", response_model=UserSchema)
async def protected_view(
    user: UserSchema = Depends(get_current_user_with_access_token),
) -> UserSchema:
    logger.info(
        f"User have successfully visited the protected page, phone number: %s",
        user.phone_number,
    )

    return user
