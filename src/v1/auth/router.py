from fastapi import APIRouter, Depends
from redis.asyncio import Redis
from starlette import status
from starlette.responses import JSONResponse

from src.utils import select_user, update_user_with_email
from src.v1.email.utils import get_redis_pool
from src.v1.email.dependencies import validate_email_code
from src.v1.jwt.dependencies import get_current_user_with_access_token
from src.v1.jwt.utils import hash_password, set_tokens_in_response, validate_password
from src.v1.email.config import email_settings
from src.database import AsyncSessionDep
from src.utils import create_user
from src.schemas import UserSchema
from src.models import UserModel
from src.v1.email.schemas import (
    EmailPasswordFirstNameVerificationCodeSchema,
    EmailPasswordVerificationCodeSchema,
    EmailTwoPasswordsSchema
)
from src.exceptions import (
    invalid_email_code_exception,
    user_not_found_exception,
    invalid_password_exception, reset_user_password_exception
)
from src.v1.auth.exceptions import invalid_reset_password_key_exception, different_passwords_exception, current_user_yet_exists_exception

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
    user: UserSchema = await create_user(
        user=UserModel(
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
    user = await select_user(session=session, get_password=True, email=user_data.email)

    if not user:
        raise user_not_found_exception
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
    # Проверка на совпадение первого и второго пароля
    if user_data.password != user_data.password2:
        raise different_passwords_exception
    # Проверка email ключа для сброса пароля на стороне сервера и ключа, который и есть endpoint - /{key}
    if key != stored_reset_password_key:
        raise invalid_reset_password_key_exception

    await update_user_with_email(session=session, user_email=user_data.email, show_user=False, password=hash_password(password=user_data.password))

    await redis_pool.delete(reset_password_redis_key)

    return JSONResponse(
        content={"message": "Пароль был успешно обновлен."},
        status_code=status.HTTP_200_OK
    )


@router.get('/protected', response_model=UserSchema)
async def protected(
        user: UserSchema = Depends(get_current_user_with_access_token)
) -> UserSchema:
    return user
