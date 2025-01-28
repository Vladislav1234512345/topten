from starlette.responses import JSONResponse
from fastapi import APIRouter, Depends
from redis.asyncio import Redis

from .schemas import PhoneNumberPasswordSchema, PhoneNumberSchema
from .responses import verification_code_sms_response, reset_password_sms_response
from src.database import AsyncSessionDep, get_redis_pool
from .utils import generate_verification_code, generate_password
from .config import sms_settings
from src.exceptions import (
    invalid_password_exception,
    too_many_sms_requests_exception,
    user_not_found_exception,
    current_user_yet_exists_exception,
)
from src.v1.jwt.utils import validate_password
from src.v1.sms.tasks import send_sms_reset_password, send_sms_verification_code
from src.utils import select_user
import logging
from src.container import configure_logging
from src.config import logging_settings

logger = logging.getLogger(__name__)
configure_logging(level=logging_settings.logging_level)


router = APIRouter()


@router.post("/")
async def sms_verification_code_view(
    user_data: PhoneNumberSchema,
    redis_pool: Redis = Depends(get_redis_pool),
) -> JSONResponse:
    verification_code_redis_key = (
        f"{sms_settings.verification_code_key}:{user_data.phone_number}"
    )
    if await redis_pool.get(verification_code_redis_key):
        logger.warning(
            "Too many requests ('/v1/sms/verification-code'), phone number: %s",
            user_data.phone_number,
        )
        raise too_many_sms_requests_exception

    sms_code = generate_verification_code()
    send_sms_verification_code.delay(
        receiver_phone_number=str(user_data.phone_number), code=sms_code
    )
    await redis_pool.set(
        verification_code_redis_key, sms_code, ex=sms_settings.expire_time
    )
    logger.info(
        "The verification sms code has been successfully sent to user, phone number: %s",
        user_data.phone_number,
    )
    return verification_code_sms_response


# @router.post("/verification-code")
# async def verification_code_view(
#     session: AsyncSessionDep,
#     user_data: PhoneNumberPasswordSchema,
#     redis_pool: Redis = Depends(get_redis_pool),
#     is_new_account: bool = False,
# ) -> JSONResponse:
#     verification_code_redis_key = (
#         f"{sms_settings.verification_code_key}:{user_data.phone_number}"
#     )
#     if await redis_pool.get(verification_code_redis_key):
#         logger.warning(
#             "Too many requests ('/v1/sms/verification-code'), phone number: %s",
#             user_data.phone_number,
#         )
#         raise too_many_sms_requests_exception
#     user = await select_user(
#         session=session,
#         full_info=False,
#         get_password=True,
#         phone_number=user_data.phone_number,
#     )
#
#     if user:
#         if is_new_account:
#             logger.warning(
#                 "Current users has been existed yet, phone number: %s",
#                 user.phone_number,
#             )
#             raise current_user_yet_exists_exception
#         if not validate_password(
#             password=user_data.password, hashed_password=user.password  # type: ignore
#         ):
#             logger.warning(
#                 "Incorrect password, phone number: %s", user_data.phone_number
#             )
#             raise invalid_password_exception
#     else:
#         if not is_new_account:
#             raise user_not_found_exception
#
#     sms_code = generate_verification_code()
#     send_sms_verification_code.delay(
#         receiver_phone_number=str(user_data.phone_number), code=sms_code
#     )
#     await redis_pool.set(
#         verification_code_redis_key, sms_code, ex=sms_settings.expire_time
#     )
#     logger.info(
#         "The verification sms-code has been successfully sent to users, phone number: %s",
#         user_data.phone_number,
#     )
#     return verification_code_sms_response


# @router.post("/reset-password")
# async def reset_password_view(
#     session: AsyncSessionDep,
#     user_data: PhoneNumberSchema,
#     redis_pool: Redis = Depends(get_redis_pool),
# ) -> JSONResponse:
#     user = await select_user(
#         session=session, full_info=False, phone_number=user_data.phone_number
#     )
#
#     if not user:
#         logger.warning("Incorrect password, phone number: %s", user_data.phone_number)
#         raise user_not_found_exception
#     sms_reset_password_key = generate_password()
#     reset_password_redis_key = (
#         f"{sms_settings.reset_password_key}:{sms_reset_password_key}"
#     )
#     if await redis_pool.get(reset_password_redis_key):
#         logger.warning(
#             "Too many requests ('/v1/sms/reset-password'), phone number: %s",
#             user_data.phone_number,
#         )
#         raise too_many_sms_requests_exception
#     send_sms_reset_password.delay(
#         receiver_phone_number=str(user_data.phone_number), key=sms_reset_password_key
#     )
#     await redis_pool.set(
#         reset_password_redis_key,
#         str(user_data.phone_number),
#         ex=sms_settings.expire_time,
#     )
#     logger.info(
#         "The password reset sms has been successfully sent to the users, phone number: %s",
#         user_data.phone_number,
#     )
#     return reset_password_sms_response
