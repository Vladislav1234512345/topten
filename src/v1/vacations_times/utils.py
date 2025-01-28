from typing import List

from starlette.exceptions import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from src.database import AsyncSessionDep
from src.v1.vacations_times.exceptions import (
    users_vacations_times_not_found_exception,
    user_vacation_time_not_found_exception,
    update_user_vacation_time_exception,
)
from src.schemas import UserVacationTimeSchema
from src.models import UserVacationTimeModel
import logging
from src.container import configure_logging
from src.config import logging_settings


logger = logging.getLogger(__name__)
configure_logging(level=logging_settings.logging_level)


async def create_user_vacation_time(
    user_vacation_time: UserVacationTimeModel,
    session: AsyncSessionDep,
    exception: HTTPException,
) -> UserVacationTimeSchema:
    session.add(user_vacation_time)
    try:
        await session.commit()
    except Exception:
        logger.warning(
            "[DATABASE] Current user vacation time has been existed yet, user_id: %s, date: %s",
            user_vacation_time.user_id,
            user_vacation_time.vacation_date,
        )
        raise exception
    await session.refresh(user_vacation_time)
    logger.info(
        "[DATABASE] User vacation time has been successfully created, user_id: %s, user_vacation_time_id: %s, date: %s",
        user_vacation_time.user_id,
        user_vacation_time.id,
        user_vacation_time.vacation_date,
    )
    return UserVacationTimeSchema.model_validate(
        user_vacation_time, from_attributes=True
    )


async def select_users_vacations_times_instances(session: AsyncSessionDep, select_one_instance: bool = True, full_info: bool = True, **filters) -> UserVacationTimeModel | List[UserVacationTimeModel] | None:  # type: ignore
    statement = select(UserVacationTimeModel).filter_by(**filters)
    if full_info:
        statement.options(
            joinedload(UserVacationTimeModel.user),
        )
    try:
        result = await session.execute(statement)
        if select_one_instance:
            return result.scalar()
        else:
            return list(result.scalars().all())
    except:
        if select_one_instance:
            logger.warning(
                "[DATABASE] User vacation time not found, params: %s", **filters
            )
            raise user_vacation_time_not_found_exception
        else:
            logger.warning(
                "[DATABASE] Users vacations times not found, params: %s", **filters
            )
            raise users_vacations_times_not_found_exception


async def select_user_vacation_time(  # type: ignore
    session: AsyncSessionDep, full_info: bool = False, **filters
) -> UserVacationTimeSchema:
    user_vacation_time = await select_users_vacations_times_instances(
        session=session, select_one_instance=True, full_info=full_info, **filters
    )

    if not user_vacation_time:
        logger.warning("[DATABASE] User vacation time not found, params: %s", **filters)
        raise user_vacation_time_not_found_exception

    logger.info(
        "[DATABASE] User vacation time has been successfully selected, user_id: %s, user_vacation_time_id: %s, date: %s",
        user_vacation_time.user_id,  # type: ignore
        user_vacation_time.id,  # type: ignore
        user_vacation_time.vacation_date,  # type: ignore
    )
    return UserVacationTimeSchema.model_validate(
        user_vacation_time, from_attributes=True
    )


async def update_user_vacation_time(  # type: ignore
    session: AsyncSessionDep,
    user_vacation_time_id: int,
    user_id: int,
    show_user: bool = False,
    **attrs
) -> UserVacationTimeSchema:
    user_vacation_time = await select_users_vacations_times_instances(
        session=session,
        select_one_instance=True,
        full_info=False,
        id=user_vacation_time_id,
        user_id=user_id,
    )
    if not user_vacation_time:
        logger.warning(
            "[DATABASE] User vacation time not found, user_id: %s, user_vacation_time_id: %s",
            user_id,
            user_vacation_time_id,
        )
        raise user_vacation_time_not_found_exception

    for key, value in attrs.items():
        if hasattr(user_vacation_time, key):
            setattr(user_vacation_time, key, value)

    try:
        await session.commit()
    except Exception:
        logger.error(
            "[DATABASE] Failed to update the user vacation time, user_id: %s, user_vacation_time_id: %S",
            user_id,
            user_vacation_time_id,
        )
        raise update_user_vacation_time_exception

    await session.refresh(user_vacation_time)

    logger.info(
        "[DATABASE] User vacation time has been successfully updated, user_id: %s, user_vacation_time_id: %s and attrs: %s",
        user_id,
        user_vacation_time_id,
        **attrs
    )

    if show_user:

        return UserVacationTimeSchema.model_validate(
            user_vacation_time, from_attributes=True
        )


async def select_users_vacations_times(  # type: ignore
    session: AsyncSessionDep, full_info: bool = False, **filters
) -> List[UserVacationTimeSchema]:
    users_vacations_dates = await select_users_vacations_times_instances(
        session=session, full_info=full_info, select_one_instance=False, **filters
    )

    if not users_vacations_dates:
        logger.warning(
            "[DATABASE] Users vacations times not found, params: %s", **filters
        )
        raise users_vacations_times_not_found_exception

    logger.info(
        "[DATABASE] Users vacations times have been successfully selected with params: %s",
        **filters
    )
    validated_users_vacations_times = [UserVacationTimeSchema.model_validate(user_vacation_time, from_attributes=True) for user_vacation_time in users_vacations_dates]  # type: ignore

    return validated_users_vacations_times


async def delete_user_vacation_time(session: AsyncSessionDep, **filters) -> bool:  # type: ignore
    user_vacation_time = await select_users_vacations_times_instances(
        session=session, full_info=False, select_one_instance=True, **filters
    )

    if not user_vacation_time:
        logger.warning("[DATABASE] User vacation time not found, params: %s", **filters)
        raise user_vacation_time_not_found_exception

    await session.delete(user_vacation_time)

    logger.info(
        "[DATABASE] User vacation time has been successfully deleted with params: %s",
        **filters
    )

    return True
