from fastapi import APIRouter, Depends
from sqlmodel import select
from starlette.responses import JSONResponse
from starlette import status
from redis.asyncio import Redis

from functions import create_db_table_instance
from models import User
from database import AsyncSessionDep
from api.v1.email.utils import get_redis_pool
from api.v1.email.validators import validate_email_code
from api.v1.email.exceptions import invalid_email_code_exception
from .validators import get_current_auth_user_for_access, get_current_auth_user_for_refresh
from .utils import set_tokens_in_response, validate_password, hash_password
from .schemas import UserLoginSchema, UserSignupSchema
from .exceptions import unauthorized_exception


router = APIRouter()


@router.post('/signup')
async def signup(
        session: AsyncSessionDep,
        user_data: UserSignupSchema,
        redis_pool: Redis = Depends(get_redis_pool),
) -> JSONResponse:
    email_code = validate_email_code(email_code=user_data.email_code)

    stored_code: str = await redis_pool.get(user_data.email)

    from config import logger
    logger.info(f"stored_code = {stored_code}")
    logger.info(f"email_code = {email_code}")
    if stored_code != email_code:
        raise invalid_email_code_exception

    user = await create_db_table_instance(
        instance=User(
            email=user_data.email,
            password=hash_password(password=user_data.password),
            first_name=user_data.first_name
        ),
        session=session
    )

    await redis_pool.delete(user_data.email)

    response: JSONResponse = JSONResponse(
        content={"message": "Регистрация прошла успешно"},
        status_code=status.HTTP_201_CREATED
    )

    return set_tokens_in_response(response=response, user=user)


@router.post('/login')
async def login(
    session: AsyncSessionDep,
    user_data: UserLoginSchema,
    redis_pool: Redis = Depends(get_redis_pool),
) -> JSONResponse:
    email_code = validate_email_code(email_code=user_data.email_code)
    stored_code: str = await redis_pool.get(user_data.email)

    from config import logger
    logger.info(f"stored_code = {stored_code}")
    logger.info(f"email_code = {email_code}")

    if stored_code != email_code:
        raise invalid_email_code_exception

    statement = select(User).filter_by(email=user_data.email)
    try:
        result = await session.execute(statement)
    except:
        raise unauthorized_exception
    user = result.scalar()

    if not user:
        raise unauthorized_exception

    if not validate_password(password=user_data.password, hashed_password=user.password):
        raise unauthorized_exception

    await redis_pool.delete(user_data.email)

    response: JSONResponse = JSONResponse(
        content={"message": "Авторизация прошла успешно"},
        status_code=status.HTTP_200_OK
    )

    return set_tokens_in_response(response=response, user=user)


@router.post('/refresh')
def refresh(
    user: User = Depends(get_current_auth_user_for_refresh)
) -> JSONResponse:

    response: JSONResponse = JSONResponse(
        content={"message": "Токены успешно обновлены"},
        status_code=status.HTTP_200_OK
    )

    return set_tokens_in_response(response=response, user=user)
