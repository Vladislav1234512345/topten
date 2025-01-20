from fastapi import HTTPException
from sqlalchemy import select

from src.schemas import UserSchema, UserPasswordSchema
from src.database import AsyncSessionDep
from src.models import UserModel
from src.exceptions import user_not_found_exception, reset_user_password_exception
import logging
from src.container import configure_logging
from src.config import logging_settings

logger = logging.getLogger(__name__)
configure_logging(level=logging_settings.logging_level)


async def create_user(
    user: UserModel, session: AsyncSessionDep, exception: HTTPException
) -> UserSchema:
    session.add(user)
    try:
        await session.commit()
    except Exception:
        logger.warning("Current user has been existed yet, email: %s", user.email)
        raise exception
    await session.refresh(user)
    logger.info(
        "User has been successfully created, id: %s, email: %s", user.id, user.email
    )
    return UserSchema.model_validate(user, from_attributes=True)


async def select_user_instance(session: AsyncSessionDep, **filters) -> UserModel | None:  # type: ignore
    statement = select(UserModel).filter_by(**filters)
    try:
        result = await session.execute(statement)
        user = result.scalar()
    except:
        logger.warning("User not found, params: %s", filters)
        raise user_not_found_exception

    return user


async def select_user(  # type: ignore
    session: AsyncSessionDep, get_password: bool = False, **filters
) -> UserPasswordSchema | UserSchema | None:
    user = await select_user_instance(session=session, **filters)

    if not user:
        return None

    if get_password:
        logger.info(
            "User has been successfully selected with password, id: %s, email: %s",
            user.id,
            user.email,
        )
        return UserPasswordSchema.model_validate(user, from_attributes=True)
    else:
        logger.info(
            "User has been successfully selected, id: %s, email: %s",
            user.id,
            user.email,
        )
        return UserSchema.model_validate(user, from_attributes=True)


async def update_user_with_email(  # type: ignore
    session: AsyncSessionDep, user_email: str, show_user: bool = False, **attrs
) -> UserSchema | None:
    user = await select_user_instance(session=session, email=user_email)
    if not user:
        logger.warning("User not found, email: %s", user_email)
        raise user_not_found_exception

    for key, value in attrs.items():
        if hasattr(user, key):
            setattr(user, key, value)

    try:
        await session.commit()
    except Exception:
        logger.error("Failed to update the user's password, email: %s", user_email)
        raise reset_user_password_exception

    if not show_user:
        return None

    await session.refresh(user)

    return UserPasswordSchema.model_validate(user, from_attributes=True)
