from fastapi import HTTPException
from pydantic import EmailStr
from sqlalchemy import select

from src.schemas import UserSchema, UserPasswordSchema
from src.database import AsyncSessionDep
from src.models import UserModel
from src.exceptions import user_not_found_exception, reset_user_password_exception
from src.container import logger


async def create_user(user: UserModel, session: AsyncSessionDep, exception: HTTPException) -> UserSchema:
    logger.info(f"{user.email=}")
    session.add(user)
    try:
        await session.commit()
    except Exception:
        raise exception
    await session.refresh(user)
    logger.info(f"{user.email=}")


    return UserSchema.model_validate(user, from_attributes=True)


async def select_user_instance(session: AsyncSessionDep, **filters) -> UserModel:
    statement = select(UserModel).filter_by(**filters)
    try:
        result = await session.execute(statement)
    except:
        raise user_not_found_exception
    user = result.scalar_one_or_none()

    return user


async def select_user(session: AsyncSessionDep, get_password: bool = False, **filters) -> UserPasswordSchema | UserSchema | None:
    user = await select_user_instance(session=session, **filters)

    if not user:
        return None

    if get_password:
        return UserPasswordSchema.model_validate(user, from_attributes=True)
    else:
        return UserSchema.model_validate(user, from_attributes=True)


async def update_user_with_email(session: AsyncSessionDep, user_email: EmailStr, show_user: bool=False, **attrs) -> UserSchema | None:
    user = await select_user_instance(session=session, email=user_email)
    from src.container import logger
    logger.info(f"{user=}")
    if not user:
        raise user_not_found_exception

    for key, value in attrs.items():
        if hasattr(user, key):
            logger.info(f"{key=}")
            logger.info(f"{value=}")
            setattr(user, key, value)
            logger.info(f"{user=}")

    try:
        await session.commit()
    except Exception:
        raise reset_user_password_exception

    if not show_user:
        return None

    session.refresh(user)

    return UserPasswordSchema.model_validate(user, from_attributes=True)






