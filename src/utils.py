import logging
from typing import List

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import joinedload, selectinload

from src.config import logging_settings
from src.container import configure_logging
from src.database import AsyncSessionDep
from src.exceptions import (
    user_not_found_exception,
    users_not_found_exception,
    reset_user_password_exception,
)
from src.models import UserModel
from src.schemas import (
    UserSchema,
    UserPasswordSchema,
    UserFullInfoSchema,
    UserPasswordFullInfoSchema,
)

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
            "[DATABASE] Current user has been existed yet, phone number: %s",
            user.phone_number,
        )
        raise exception
    await session.refresh(user)
    logger.info(
        "[DATABASE] User has been successfully created, user_id: %s, phone number: %s",
        user.id,
        user.phone_number,
    )
    return UserSchema.model_validate(user, from_attributes=True)


async def select_users_instances(session: AsyncSessionDep, exclude_none: bool = True, select_one_instance: bool = True, full_info: bool = True, **filters) -> UserModel | List[UserModel] | None:  # type: ignore

    if full_info:
        statement = (
            select(UserModel)
            .options(
                joinedload(UserModel.profile),
                joinedload(UserModel.break_time),
                selectinload(UserModel.cards),
                selectinload(UserModel.vacations_dates),
                selectinload(UserModel.vacations_times),
                selectinload(UserModel.week_days),
                selectinload(UserModel.applications),
                selectinload(UserModel.sent_reviews),
                selectinload(UserModel.activities),
            )
            .filter_by(**filters)
        )
    else:
        statement = select(UserModel).filter_by(**filters)
    try:
        result = await session.execute(statement)
        if select_one_instance:
            return result.scalar()
        else:
            return list(result.scalars().all())
    except:
        if exclude_none:
            if select_one_instance:
                logger.warning("[DATABASE] User not found, params: %s", filters)
            else:
                logger.warning("[DATABASE] Users not found, params: %s", filters)
                raise users_not_found_exception
        else:
            return None


async def select_user(  # type: ignore
    session: AsyncSessionDep,
    full_info: bool = False,
    exclude_none: bool = True,
    get_password: bool = False,
    **filters,
) -> (
    UserPasswordSchema
    | UserSchema
    | UserFullInfoSchema
    | UserPasswordFullInfoSchema
    | None
):
    user = await select_users_instances(
        session=session,
        exclude_none=exclude_none,
        select_one_instance=True,
        full_info=full_info,
        **filters,
    )
    if not user:
        logger.warning("[DATABASE] User not found, params: %s", filters)
        if exclude_none:
            raise user_not_found_exception
        else:
            return None

    if get_password:
        logger.info(
            "[DATABASE] User has been successfully selected with password, user_id: %s, phone number: %s",
            user.id,  # type: ignore
            user.phone_number,  # type: ignore
        )
        if full_info:
            return UserPasswordFullInfoSchema.model_validate(user, from_attributes=True)
        else:
            return UserPasswordSchema.model_validate(user, from_attributes=True)
    else:
        logger.info(
            "[DATABASE] User has been successfully selected, user_id: %s, phone number: %s",
            user.id,  # type: ignore
            user.phone_number,  # type: ignore
        )
        if full_info:
            return UserFullInfoSchema.model_validate(user, from_attributes=True)
        else:
            return UserSchema.model_validate(user, from_attributes=True)


async def update_user_with_phone_number(  # type: ignore
    session: AsyncSessionDep, user_phone_number: str, show_user: bool = False, **attrs
) -> UserSchema | None:
    user = await select_users_instances(
        session=session,
        select_one_instance=True,
        full_info=False,
        phone_number=user_phone_number,
    )
    if not user:
        logger.warning("[DATABASE] User not found, phone number: %s", user_phone_number)
        raise user_not_found_exception

    for key, value in attrs.items():
        if hasattr(user, key):
            setattr(user, key, value)

    try:
        await session.commit()
    except Exception:
        logger.error(
            "[DATABASE] Failed to update the user's password, phone number: %s",
            user_phone_number,
        )
        raise reset_user_password_exception

    if not show_user:
        return None

    await session.refresh(user)

    logger.info(
        "[DATABASE] User has been successfully updated, phone number: %s and attrs: %s",
        user_phone_number,
        **attrs,
    )

    return UserPasswordSchema.model_validate(user, from_attributes=True)


async def update_user_with_id(  # type: ignore
    session: AsyncSessionDep, user_id: int, show_user: bool = False, **attrs
) -> UserSchema | None:
    user = await select_users_instances(
        session=session, select_one_instance=True, full_info=False, id=user_id
    )
    if not user:
        logger.warning("[DATABASE] User not found, user_id: %s", user_id)
        raise user_not_found_exception

    for key, value in attrs.items():
        if hasattr(user, key):
            setattr(user, key, value)

    try:
        await session.commit()
    except Exception:
        logger.error("[DATABASE] Failed to update the user, user_id: %s", user_id)
        from src.v1.users.exceptions import update_user_exception

        raise update_user_exception

    if not show_user:
        return None

    await session.refresh(user)

    logger.info(
        "[DATABASE] User has been successfully updated, user_id: %s and attrs: %s",
        user_id,
        **attrs,
    )

    return UserPasswordSchema.model_validate(user, from_attributes=True)


async def select_users(  # type: ignore
    session: AsyncSessionDep, full_info: bool = False, **filters
) -> List[UserSchema] | None:
    users = await select_users_instances(
        session=session, full_info=full_info, select_one_instance=False, **filters
    )

    if not users:
        logger.warning("[DATABASE] Users not found, params: %s", filters)
        raise user_not_found_exception

    logger.info(
        "[DATABASE] Users have been successfully selected with params: %s", filters
    )
    if full_info:
        validated_users = [
            UserFullInfoSchema.model_validate(user, from_attributes=True) for user in users  # type: ignore
        ]
    else:
        validated_users = [
            UserSchema.model_validate(user, from_attributes=True) for user in users  # type: ignore
        ]

    return validated_users


async def delete_user(session: AsyncSessionDep, **filters) -> bool:  # type: ignore
    user = await select_users_instances(
        session=session, full_info=False, select_one_instance=True, **filters
    )

    if not user:
        logger.warning("[DATABASE] User not found, params: %s", filters)
        raise user_not_found_exception

    await session.delete(user)

    logger.info(
        "[DATABASE] User has been successfully deleted with params: %s", filters
    )

    return True
