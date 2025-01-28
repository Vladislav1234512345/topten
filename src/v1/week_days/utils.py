from typing import List

from starlette.exceptions import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from src.database import AsyncSessionDep
from src.v1.week_days.exceptions import (
    users_week_days_not_found_exception,
    user_week_day_not_found_exception,
    update_user_week_day_exception,
)
from src.schemas import UserWeekDaySchema
from src.models import UserWeekDayModel, WeekDayEnum
import logging
from src.container import configure_logging
from src.config import logging_settings


logger = logging.getLogger(__name__)
configure_logging(level=logging_settings.logging_level)


async def create_user_week_day(
    user_week_day: UserWeekDayModel, session: AsyncSessionDep, exception: HTTPException
) -> UserWeekDaySchema:
    session.add(user_week_day)
    try:
        await session.commit()
    except Exception:
        logger.warning(
            "[DATABASE] Current user week day has been existed yet, user_id: %s, week_day %s",
            user_week_day.user_id,
            user_week_day.week_day,
        )
        raise exception
    await session.refresh(user_week_day)
    logger.info(
        "[DATABASE] User week day has been successfully created, user_id: %s, user_week_day_id: %s, week_day: %s",
        user_week_day.user_id,
        user_week_day.id,
        user_week_day.week_day,
    )
    return UserWeekDaySchema.model_validate(user_week_day, from_attributes=True)


async def select_users_week_days_instances(session: AsyncSessionDep, select_one_instance: bool = True, full_info: bool = True, **filters) -> UserWeekDayModel | List[UserWeekDayModel] | None:  # type: ignore
    statement = select(UserWeekDayModel).filter_by(**filters)
    if full_info:
        statement.options(
            joinedload(UserWeekDayModel.user),
        )
    try:
        result = await session.execute(statement)
        if select_one_instance:
            return result.scalar()
        else:
            return list(result.scalars().all())
    except:
        if select_one_instance:
            logger.warning("[DATABASE] User week day not found, params: %s", **filters)
            raise user_week_day_not_found_exception
        else:
            logger.warning(
                "[DATABASE] Users week days not found, params: %s", **filters
            )
            raise users_week_days_not_found_exception


async def select_user_week_day(  # type: ignore
    session: AsyncSessionDep, full_info: bool = False, **filters
) -> UserWeekDaySchema:
    user_week_day = await select_users_week_days_instances(
        session=session, select_one_instance=True, full_info=full_info, **filters
    )

    if not user_week_day:
        logger.warning("[DATABASE] User week day not found, params: %s", **filters)
        raise user_week_day_not_found_exception

    logger.info(
        "[DATABASE] User week day has been successfully selected, user_id: %s, user_week_day_id: %s, week_day: %s",
        user_week_day.user_id,  # type: ignore
        user_week_day.id,  # type: ignore
        user_week_day.week_day,  # type: ignore
    )
    return UserWeekDaySchema.model_validate(user_week_day, from_attributes=True)


async def update_user_week_day(  # type: ignore
    session: AsyncSessionDep,
    week_day: WeekDayEnum,
    user_id: int,
    show_user: bool = False,
    **attrs
) -> UserWeekDaySchema:
    user_week_day = await select_users_week_days_instances(
        session=session,
        select_one_instance=True,
        full_info=False,
        week_day=week_day,
        user_id=user_id,
    )
    if not user_week_day:
        logger.warning(
            "[DATABASE] User week day not found, user_id: %s, week_day: %s",
            user_id,
            week_day,
        )
        raise user_week_day_not_found_exception

    for key, value in attrs.items():
        if hasattr(user_week_day, key):
            setattr(user_week_day, key, value)

    try:
        await session.commit()
    except Exception:
        logger.error(
            "[DATABASE] Failed to update the user week day, user_id: %s, week_day: %S",
            user_id,
            week_day,
        )
        raise update_user_week_day_exception

    if show_user:

        await session.refresh(user_week_day)

        logger.info(
            "[DATABASE] User week day has been successfully updated, user_id: %s, week_day: %s and attrs: %s",
            user_id,
            week_day,
            **attrs
        )

        return UserWeekDaySchema.model_validate(user_week_day, from_attributes=True)


async def select_users_week_days(  # type: ignore
    session: AsyncSessionDep, full_info: bool = False, **filters
) -> List[UserWeekDaySchema]:
    users_week_days = await select_users_week_days_instances(
        session=session, full_info=full_info, select_one_instance=False, **filters
    )

    if not users_week_days:
        logger.warning("[DATABASE] Users week days not found, params: %s", **filters)
        raise users_week_days_not_found_exception

    logger.info(
        "[DATABASE] Users week days have been successfully selected with params: %s",
        **filters
    )
    validated_users_week_days = [UserWeekDaySchema.model_validate(user_week_day, from_attributes=True) for user_week_day in users_week_days]  # type: ignore

    return validated_users_week_days


async def delete_user_week_day(session: AsyncSessionDep, **filters) -> bool:  # type: ignore
    user_week_day = await select_users_week_days_instances(
        session=session, full_info=False, select_one_instance=True, **filters
    )

    if not user_week_day:
        logger.warning("[DATABASE] User week day not found, params: %s", **filters)
        raise user_week_day_not_found_exception

    await session.delete(user_week_day)

    logger.info(
        "[DATABASE] User week day has been successfully deleted with params: %s",
        **filters
    )

    return True
