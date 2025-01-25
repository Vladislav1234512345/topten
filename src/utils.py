from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from src.schemas import UserSchema, UserPasswordSchema, ProfileSchema
from src.database import AsyncSessionDep
from src.models import UserModel, ProfileModel
from src.exceptions import (
    user_not_found_exception,
    reset_user_password_exception,
    profile_not_found_exception,
    update_profile_exception,
)
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
        logger.warning(
            "Current user has been existed yet, phone number: %s", user.phone_number
        )
        raise exception
    await session.refresh(user)
    logger.info(
        "User has been successfully created, user_id: %s, phone number: %s",
        user.id,
        user.phone_number,
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
            "User has been successfully selected with password, user_id: %s, phone number: %s",
            user.id,
            user.phone_number,
        )
        return UserPasswordSchema.model_validate(user, from_attributes=True)
    else:
        logger.info(
            "User has been successfully selected, user_id: %s, phone number: %s",
            user.id,
            user.phone_number,
        )
        return UserSchema.model_validate(user, from_attributes=True)


async def update_user_with_phone_number(  # type: ignore
    session: AsyncSessionDep, user_phone_number: str, show_user: bool = False, **attrs
) -> UserSchema | None:
    user = await select_user_instance(session=session, phone_number=user_phone_number)
    if not user:
        logger.warning("User not found, phone number: %s", user_phone_number)
        raise user_not_found_exception

    for key, value in attrs.items():
        if hasattr(user, key):
            setattr(user, key, value)

    try:
        await session.commit()
    except Exception:
        logger.error(
            "Failed to update the user's password, phone number: %s", user_phone_number
        )
        raise reset_user_password_exception

    if not show_user:
        return None

    await session.refresh(user)

    return UserPasswordSchema.model_validate(user, from_attributes=True)


async def create_profile(
    profile: ProfileModel, session: AsyncSessionDep, exception: HTTPException
) -> ProfileSchema:
    session.add(profile)
    try:
        await session.commit()
    except Exception:
        logger.warning(
            "Current profile has been existed yet, first name: %s",
            profile.first_name,
        )
        raise exception
    await session.refresh(profile)
    logger.info(
        "Profile has been successfully created, profile_id: %s, user_id: %s, first name: %s",
        profile.id,
        profile.user_id,
        profile.first_name,
    )
    return ProfileSchema.model_validate(profile, from_attributes=True)


async def select_profile_instance(session: AsyncSessionDep, **filters) -> ProfileModel | None:  # type: ignore
    statement = (
        select(ProfileModel).options(joinedload(ProfileModel.user)).filter_by(**filters)
    )
    try:
        result = await session.execute(statement)
        profile = result.scalar()
    except:
        logger.warning("Profile not found, params: %s", filters)
        raise profile_not_found_exception

    return profile


async def select_profile(  # type: ignore
    session: AsyncSessionDep, **filters
) -> ProfileSchema | None:
    profile = await select_profile_instance(session=session, **filters)

    if not profile:
        raise profile_not_found_exception

    logger.info(
        "Profile has been successfully selected, profile_id: %s, user_id: %s, phone number: %s",
        profile.id,
        profile.user_id,
        profile.user.phone_number,
    )
    return ProfileSchema.model_validate(profile, from_attributes=True)


async def update_profile_with_id(  # type: ignore
    session: AsyncSessionDep, profile_id: int, **attrs
) -> ProfileSchema | None:
    profile = await select_profile_instance(session=session, id=profile_id)
    if not profile:
        logger.warning("Profile not found, profile_id: %s", profile_id)
        raise profile_not_found_exception

    for key, value in attrs.items():
        if hasattr(profile, key):
            setattr(profile, key, value)

    try:
        await session.commit()
    except Exception:
        logger.error("Failed to update the profile, profile_id: %s", profile_id)
        raise update_profile_exception

    await session.refresh(profile)

    return ProfileSchema.model_validate(profile, from_attributes=True)
