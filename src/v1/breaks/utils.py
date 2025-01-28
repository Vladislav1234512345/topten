from typing import List

from starlette.exceptions import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import selectinload, joinedload

from src.database import AsyncSessionDep
from src.v1.breaks.exceptions import (
    users_breaks_not_found_exception,
    user_break_not_found_exception,
    update_user_break_exception,
)
from src.v1.breaks.schemas import UserBreakSchema
from src.models import UserBreakModel
import logging
from src.container import configure_logging
from src.config import logging_settings


logger = logging.getLogger(__name__)
configure_logging(level=logging_settings.logging_level)


async def create_user_break(
    user_break: UserBreakModel, session: AsyncSessionDep, exception: HTTPException
) -> UserBreakSchema:
    session.add(user_break)
    try:
        await session.commit()
    except Exception:
        logger.warning(
            "[DATABASE] Current user break has been existed yet, name %s",
            user_break.break_time,
        )
        raise exception
    await session.refresh(user_break)
    logger.info(
        "[DATABASE] User break has been successfully created, user_id: %s, user_break_id: %s, name: %s",
        user_break.user_id,
        user_break.id,
        user_break.break_time,
    )
    return UserBreakSchema.model_validate(user_break, from_attributes=True)


async def select_users_breaks_instances(session: AsyncSessionDep, select_one_instance: bool = True, full_info: bool = True, **filters) -> UserBreakModel | List[UserBreakModel] | None:  # type: ignore
    statement = select(UserBreakModel).filter_by(**filters)
    if full_info:
        statement.options(
            joinedload(UserBreakModel.user),
        )
    try:
        result = await session.execute(statement)
        if select_one_instance:
            return result.scalar()
        else:
            return list(result.scalars().all())
    except:
        if select_one_instance:
            logger.warning("[DATABASE] User break not found, params: %s", **filters)
            raise user_break_not_found_exception
        else:
            logger.warning("[DATABASE] Users breaks not found, params: %s", **filters)
            raise users_breaks_not_found_exception


async def select_user_break(  # type: ignore
    session: AsyncSessionDep, full_info: bool = False, **filters
) -> UserBreakSchema:
    user_break = await select_users_breaks_instances(
        session=session, select_one_instance=True, full_info=full_info, **filters
    )

    if not user_break:
        logger.warning("[DATABASE] User break not found, params: %s", **filters)
        raise user_break_not_found_exception

    logger.info(
        "[DATABASE] User break has been successfully selected, user_id: %s, user_break_id: %s, name: %s",
        user_break.user_id,  # type: ignore
        user_break.id,  # type: ignore
        user_break.name,  # type: ignore
    )
    return UserBreakSchema.model_validate(user_break, from_attributes=True)


async def update_user_break(  # type: ignore
    session: AsyncSessionDep, user_id: int, show_user: bool = False, **attrs
) -> UserBreakSchema:
    user_break = await select_users_breaks_instances(
        session=session, select_one_instance=True, full_info=False, user_id=user_id
    )
    if not user_break:
        logger.warning("[DATABASE] User break not found, user_id: %s", user_id)
        raise user_break_not_found_exception

    for key, value in attrs.items():
        if hasattr(user_break, key):
            setattr(user_break, key, value)

    try:
        await session.commit()
    except Exception:
        logger.error("[DATABASE] Failed to update the user break, user_id: %s", user_id)
        raise update_user_break_exception

    if show_user:

        await session.refresh(user_break)

        logger.info(
            "[DATABASE] User break has been successfully updated, user_id: %s and attrs: %s",
            user_id,
            **attrs
        )

        return UserBreakSchema.model_validate(user_break, from_attributes=True)


async def select_users_breaks(  # type: ignore
    session: AsyncSessionDep, full_info: bool = False, **filters
) -> List[UserBreakSchema]:
    users_breaks = await select_users_breaks_instances(
        session=session, full_info=full_info, select_one_instance=False, **filters
    )

    if not users_breaks:
        logger.warning("[DATABASE] Users breaks not found, params: %s", **filters)
        raise users_breaks_not_found_exception

    logger.info(
        "[DATABASE] Users breaks have been successfully selected with params: %s",
        **filters
    )
    validated_users_breaks = [UserBreakSchema.model_validate(activity, from_attributes=True) for activity in users_breaks]  # type: ignore

    return validated_users_breaks


async def delete_user_break(session: AsyncSessionDep, **filters) -> bool:  # type: ignore
    user_break = await select_users_breaks_instances(
        session=session, full_info=False, select_one_instance=True, **filters
    )

    if not user_break:
        logger.warning("[DATABASE] User break not found, params: %s", **filters)
        raise user_break_not_found_exception

    await session.delete(user_break)

    logger.info(
        "[DATABASE] User break has been successfully deleted with params: %s", **filters
    )

    return True
