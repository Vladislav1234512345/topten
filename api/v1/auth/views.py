from fastapi import APIRouter, Depends
from redis.asyncio import Redis
from sqlmodel import select
from starlette import status
from starlette.responses import JSONResponse

from api.v1.email.utils import get_redis_pool
from api.v1.email.validators import validate_email_code
from api.v1.jwt.utils import hash_password, set_tokens_in_response, validate_password
from config import email_settings
from database import AsyncSessionDep
from functions import create_db_table_instance
from models import User
from api.v1.email.schemas import (
    EmailPasswordFirstNameVerificationCodeSchema,
    EmailPasswordVerificationCodeSchema,
    EmailTwoPasswordsSchema
)
from exceptions import (
    invalid_email_code_exception,
    current_user_yet_exists_exception,
    invalid_email_exception,
    invalid_password_exception,
    different_passwords_exception,
    invalid_reset_password_key_exception,
    reset_user_password_exception
)

router = APIRouter()


@router.post('/signup')
async def signup(
        session: AsyncSessionDep,
        user_data: EmailPasswordFirstNameVerificationCodeSchema,
        redis_pool: Redis = Depends(get_redis_pool),
) -> JSONResponse:
    verification_code_redis_key = f"{email_settings.verification_code_name}:{user_data.email}"
    # Валидация email кода
    email_code = validate_email_code(email_code=user_data.email_code)
    # Получение email кода из redis
    stored_code: str = await redis_pool.get(verification_code_redis_key)
    # Проверка email кода на стороне сервера и кода, который отправил пользователь
    if stored_code != email_code:
        raise invalid_email_code_exception
    # Создание экземпляра пользователя в базе данных
    user: User = await create_db_table_instance(
        instance=User(
            email=user_data.email,
            password=hash_password(password=user_data.password),
            first_name=user_data.first_name
        ),
        session=session,
        exception=current_user_yet_exists_exception
    )
    # Удаление email кода из redis
    await redis_pool.delete(verification_code_redis_key)
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
    verification_code_redis_key = f"{email_settings.verification_code_name}:{user_data.email}"
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
    # Получение email кода из redis
    stored_code: str = await redis_pool.get(verification_code_redis_key)
    # Проверка email кода на стороне сервера и кода, который отправил пользователь
    if stored_code != email_code:
        raise invalid_email_code_exception
    # Удаление email кода из redis
    await redis_pool.delete(verification_code_redis_key)
    # Статус код и контент ответа
    response: JSONResponse = JSONResponse(
        content={"message": "Авторизация прошла успешно."},
        status_code=status.HTTP_200_OK
    )
    # Настройка токенов и ответа сервера
    return set_tokens_in_response(response=response, user=user)


@router.post('/reset-password/{key}')
async def reset_password(
        key: str,
        session: AsyncSessionDep,
        user_data: EmailTwoPasswordsSchema,
        redis_pool: Redis = Depends(get_redis_pool)
) -> JSONResponse:
    reset_password_redis_key = f"{email_settings.reset_password_name}:{user_data.email}"
    # Получение email кода из redis
    stored_reset_password_key: str = await redis_pool.get(reset_password_redis_key)
    # Поиск пользователя в базе данных по почте
    statement = select(User).filter_by(email=user_data.email)
    try:
        result = await session.execute(statement)
    except:
        raise invalid_email_exception
    user = result.scalar()

    if not user:
        raise invalid_email_exception
    # Проверка совпадают ли первый и второй пароль
    if user_data.password != user_data.password2:
        raise different_passwords_exception
    # Проверка email ключа для сброса пароля на стороне сервера и ключа, который и есть endpoint - /{key}
    if key != stored_reset_password_key:
        raise invalid_reset_password_key_exception
    # Обновление пароля пользователя
    user.password = hash_password(user_data.password)
    # Сохранение записи пользователя с новым паролем
    try:
        await session.commit()
    except Exception:
        raise reset_user_password_exception

    return JSONResponse(
        content={"message": "Пароль был успешно обновлен."},
        status_code=status.HTTP_200_OK
    )
