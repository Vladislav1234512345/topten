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
from .validators import get_current_auth_user_for_access, get_current_auth_user_for_refresh
from .utils import set_tokens_in_response, validate_password, hash_password
from api.v1.email.schemas import EmailPasswordFirstNameVerificationCodeSchema, EmailPasswordVerificationCodeSchema
from exceptions import current_user_yet_exists_exception, invalid_password_exception, invalid_email_exception, \
    invalid_email_code_exception

router = APIRouter()


@router.post('/signup')
async def signup(
        session: AsyncSessionDep,
        user_data: EmailPasswordFirstNameVerificationCodeSchema,
        redis_pool: Redis = Depends(get_redis_pool),
) -> JSONResponse:
    # Получение email кода из redis
    stored_code: str = await redis_pool.get(user_data.email)
    # Валидация email кода
    email_code = validate_email_code(email_code=user_data.email_code)
    # Проверка email кода на стороне сервера и кода, который отправил пользователь
    if stored_code != email_code:
        raise invalid_email_code_exception
    # Создание экземпляра пользователя в базе данных
    user = await create_db_table_instance(
        instance=User(
            email=user_data.email,
            password=hash_password(password=user_data.password),
            first_name=user_data.first_name
        ),
        session=session,
        exception=current_user_yet_exists_exception
    )
    # Удаление email кода из redis
    await redis_pool.delete(user_data.email)
    # Статус код и контент ответа
    response: JSONResponse = JSONResponse(
        content={"message": "Регистрация прошла успешно."},
        status_code=status.HTTP_201_CREATED
    )
    # Настройка токенов и ответа сервера
    return set_tokens_in_response(response=response, user=user)


@router.post('/login')
async def login(
    session: AsyncSessionDep,
    user_data: EmailPasswordVerificationCodeSchema,
    redis_pool: Redis = Depends(get_redis_pool),
) -> JSONResponse:
    # Получение email кода из redis
    stored_code: str = await redis_pool.get(user_data.email)
    # Поиск пользователя в базе данных по почте
    statement = select(User).filter_by(email=user_data.email)
    try:
        result = await session.execute(statement)
    except:
        raise invalid_email_exception
    user = result.scalar()

    if not user:
        raise invalid_email_exception
    # Проверка пароля пользователя из базы даннх и пароля, который отправил сам пользователь
    if not validate_password(password=user_data.password, hashed_password=user.password):
        raise invalid_password_exception
    # Валидация email кода
    email_code = validate_email_code(email_code=user_data.email_code)
    # Проверка email кода на стороне сервера и кода, который отправил пользователь
    if stored_code != email_code:
        raise invalid_email_code_exception
    # Удаление email кода из redis
    await redis_pool.delete(user_data.email)
    # Статус код и контент ответа
    response: JSONResponse = JSONResponse(
        content={"message": "Авторизация прошла успешно."},
        status_code=status.HTTP_200_OK
    )
    # Настройка токенов и ответа сервера
    return set_tokens_in_response(response=response, user=user)


@router.post('/refresh')
def refresh(
    user: User = Depends(get_current_auth_user_for_refresh)
) -> JSONResponse:

    response: JSONResponse = JSONResponse(
        content={"message": "Токены успешно обновлены."},
        status_code=status.HTTP_200_OK
    )

    return set_tokens_in_response(response=response, user=user)
