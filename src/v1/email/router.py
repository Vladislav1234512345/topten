from starlette.responses import JSONResponse
from starlette import status
from fastapi import APIRouter, Depends
from redis.asyncio import Redis

from .schemas import EmailPasswordSchema, EmailSchema
from src.database import AsyncSessionDep
from .utils import generate_verification_code, get_redis_pool, generate_password
from .config import email_settings
from src.models import User
from src.exceptions import invalid_password_exception, invalid_email_exception, too_many_requests_exception
from src.v1.jwt.utils import validate_password
from src.v1.email.tasks import send_email_reset_password, send_email_verification_code
from src.utils import select_instance


router = APIRouter()


@router.post("/verification-code")
async def verification_code(
        session: AsyncSessionDep,
        user_data: EmailPasswordSchema,
        redis_pool: Redis = Depends(get_redis_pool),
) -> JSONResponse:
    verification_code_redis_key = f"{email_settings.verification_code_name}:{user_data.email}"
    # Проверка на наличие почты в redis с целью получения кода
    if await redis_pool.get(verification_code_redis_key):
        raise too_many_requests_exception
    # # Поиск пользователя в базе данных по почте
    # statement = select(User).filter_by(email=user_data.email)
    # try:
    #     result = await session.execute(statement)
    # except:
    #     raise invalid_email_exception
    # user = result.scalar()
    user = await select_instance(cls=User, session=session, email=user_data.email)

    if user:
        # Проверка пароля пользователя
        if not validate_password(password=user_data.password, hashed_password=user.password):
            raise invalid_password_exception
    # Генерация кода верификации
    email_code = generate_verification_code()
    # Вызов функции для отправки сообщения по почте с верификационным кодом
    send_email_verification_code.delay(receiver_email=user_data.email, code=email_code)
    # Установка почты и верификационного кода в redis
    await redis_pool.set(verification_code_redis_key, email_code, ex=email_settings.expire_time)

    return JSONResponse(status_code=status.HTTP_200_OK, content={"message": "Сообщение с кодом верификации успешно отправлено."})


@router.post('/reset-password')
async def reset_password(
        session: AsyncSessionDep,
        user_data: EmailSchema,
        redis_pool: Redis = Depends(get_redis_pool),
) -> JSONResponse:
    reset_password_redis_key = f"{email_settings.reset_password_name}:{user_data.email}"
    # Проверка на наличие почты в redis с целью сбросить пароль
    if await redis_pool.get(reset_password_redis_key):
        raise too_many_requests_exception
    # Поиск пользователя в базе данных по почте
    # statement = select(User).filter_by(email=user_data.email)
    # try:
    #     result = await session.execute(statement)
    # except:
    #     raise invalid_email_exception
    # user = result.scalar()
    user = await select_instance(cls=User, session=session, email=user_data.email)

    if not user:
        raise invalid_email_exception
    # Генерация ключа для сброса пароля
    email_reset_password_key = generate_password()
    # Вызов функции для отправки сообщения по почте с ключом сброса пароля
    send_email_reset_password.delay(receiver_email=user_data.email, key=email_reset_password_key)
    # Установка почты и ключа сброса пароля в redis
    await redis_pool.set(reset_password_redis_key, email_reset_password_key, ex=email_settings.expire_time)

    return JSONResponse(status_code=status.HTTP_200_OK, content={"message": "Сообщение для сброса пароля успешно отправлено."})