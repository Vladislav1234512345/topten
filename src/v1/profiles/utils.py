from typing import List

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from src.database import AsyncSessionDep
from src.v1.profiles.exceptions import (
    profile_not_found_exception,
    profiles_not_found_exception,
    update_profile_exception,
)
from src.models import ProfileModel
from src.schemas import ProfileSchema
import logging
from src.container import configure_logging
from src.config import logging_settings

logger = logging.getLogger(__name__)
configure_logging(level=logging_settings.logging_level)


async def delete_profile(session: AsyncSessionDep, **filters) -> bool:  # type: ignore
    profile = await select_profiles_instances(
        session=session, select_one_instance=True, **filters
    )

    if not profile:
        logger.warning("[DATABASE] Profile not found, params: %s", **filters)
        raise profile_not_found_exception

    await session.delete(profile)
    logger.info(
        "[DATABASE] Profile has been successfully deleted with params: %s", **filters
    )

    return True


async def create_profile(
    profile: ProfileModel, session: AsyncSessionDep, exception: HTTPException
) -> ProfileSchema:
    session.add(profile)
    try:
        await session.commit()
    except Exception:
        logger.warning(
            "[DATABASE] Current profile has been existed yet, first name: %s",
            profile.first_name,
        )
        raise exception
    await session.refresh(profile)
    logger.info(
        "[DATABASE] Profile has been successfully created, profile_id: %s, user_id: %s, first name: %s",
        profile.id,
        profile.user_id,
        profile.first_name,
    )
    return ProfileSchema.model_validate(profile, from_attributes=True)


async def select_profiles_instances(session: AsyncSessionDep, select_one_instance: bool = True, **filters) -> List[ProfileModel] | ProfileModel | None:  # type: ignore
    statement = (
        select(ProfileModel).options(joinedload(ProfileModel.user)).filter_by(**filters)
    )
    try:
        result = await session.execute(statement)
        if select_one_instance:
            return result.scalar()
        else:
            return list(result.scalars().all())
    except:
        if select_one_instance:
            logger.warning("[DATABASE] Profile not found, params: %s", **filters)
            raise profile_not_found_exception
        else:
            logger.warning("[DATABASE] Profiles not found, params: %s", **filters)
            raise profiles_not_found_exception


async def select_profile(  # type: ignore
    session: AsyncSessionDep, **filters
) -> ProfileSchema:
    profile = await select_profiles_instances(
        session=session, select_one_instance=True, **filters
    )

    if not profile:
        logger.warning("[DATABASE] Profile not found, params: %s", **filters)
        raise profile_not_found_exception

    logger.info(
        "[DATABASE] Profile has been successfully selected, profile_id: %s, user_id: %s, phone number: %s",
        profile.id,  # type: ignore
        profile.user_id,  # type: ignore
        profile.user.phone_number,  # type: ignore
    )
    return ProfileSchema.model_validate(profile, from_attributes=True)


async def update_profile_with_id(  # type: ignore
    session: AsyncSessionDep, profile_id: int, **attrs
) -> ProfileSchema:
    profile = await select_profiles_instances(
        session=session, select_one_instance=True, id=profile_id
    )
    if not profile:
        logger.warning("[DATABASE] Profile not found, profile_id: %s", profile_id)
        raise profile_not_found_exception

    for key, value in attrs.items():
        if hasattr(profile, key):
            setattr(profile, key, value)

    try:
        await session.commit()
    except Exception:
        logger.error(
            "[DATABASE] Failed to update the profile, profile_id: %s", profile_id
        )
        raise update_profile_exception

    await session.refresh(profile)

    logger.info(
        "[DATABASE] Profile has been successfully updated with profile_id: %s and attrs: %s",
        profile_id,
        **attrs
    )

    return ProfileSchema.model_validate(profile, from_attributes=True)


async def select_profiles(  # type: ignore
    session: AsyncSessionDep, **filters
) -> List[ProfileSchema]:
    profiles = await select_profiles_instances(
        session=session, select_one_instance=False, **filters
    )

    if not profiles:
        logger.warning("[DATABASE] Profiles not found, params: %s", **filters)
        raise profiles_not_found_exception

    logger.info(
        "[DATABASE] Profiles have been successfully selected with params: %s", **filters
    )
    validated_profiles = [
        ProfileSchema.model_validate(profile, from_attributes=True)
        for profile in profiles  # type: ignore
    ]

    return validated_profiles
