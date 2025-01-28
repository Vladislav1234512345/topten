from typing import List

from starlette.exceptions import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from src.database import AsyncSessionDep
from src.v1.vacations_dates.exceptions import (
    users_vacations_dates_not_found_exception,
    user_vacation_date_not_found_exception,
    update_user_vacation_date_exception,
)
from src.v1.vacations_dates.schemas import UserVacationDateSchema
from src.models import UserVacationDateModel, WeekDayEnum
import logging
from src.container import configure_logging
from src.config import logging_settings


logger = logging.getLogger(__name__)
configure_logging(level=logging_settings.logging_level)


async def create_user_vacation_date(
    user_vacation_date: UserVacationDateModel,
    session: AsyncSessionDep,
    exception: HTTPException,
) -> UserVacationDateSchema:
    session.add(user_vacation_date)
    try:
        await session.commit()
    except Exception:
        logger.warning(
            "[DATABASE] Current user vacation date has been existed yet, user_id: %s",
            user_vacation_date.user_id,
        )
        raise exception
    await session.refresh(user_vacation_date)
    logger.info(
        "[DATABASE] User vacation date has been successfully created, user_id: %s, user_vacation_date_id: %s",
        user_vacation_date.user_id,
        user_vacation_date.id,
    )
    return UserVacationDateSchema.model_validate(
        user_vacation_date, from_attributes=True
    )


async def select_users_vacations_dates_instances(session: AsyncSessionDep, select_one_instance: bool = True, full_info: bool = True, **filters) -> UserVacationDateModel | List[UserVacationDateModel] | None:  # type: ignore
    statement = select(UserVacationDateModel).filter_by(**filters)
    if full_info:
        statement.options(
            joinedload(UserVacationDateModel.user),
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
                "[DATABASE] User vacation date not found, params: %s", **filters
            )
            raise user_vacation_date_not_found_exception
        else:
            logger.warning(
                "[DATABASE] Users vacations dates not found, params: %s", **filters
            )
            raise users_vacations_dates_not_found_exception


async def select_user_vacation_date(  # type: ignore
    session: AsyncSessionDep, full_info: bool = False, **filters
) -> UserVacationDateSchema:
    user_vacation_date = await select_users_vacations_dates_instances(
        session=session, select_one_instance=True, full_info=full_info, **filters
    )

    if not user_vacation_date:
        logger.warning("[DATABASE] User vacation date not found, params: %s", **filters)
        raise user_vacation_date_not_found_exception

    logger.info(
        "[DATABASE] User vacation date has been successfully selected, user_id: %s, user_vacation_date_id: %s",
        user_vacation_date.user_id,  # type: ignore
        user_vacation_date.id,  # type: ignore
    )
    return UserVacationDateSchema.model_validate(
        user_vacation_date, from_attributes=True
    )


async def update_user_vacation_date(  # type: ignore
    session: AsyncSessionDep,
    user_vacation_date_id: int,
    user_id: int,
    show_user: bool = False,
    **attrs
) -> UserVacationDateSchema:
    user_vacation_date = await select_users_vacations_dates_instances(
        session=session,
        select_one_instance=True,
        full_info=False,
        id=user_vacation_date_id,
        user_id=user_id,
    )
    if not user_vacation_date:
        logger.warning(
            "[DATABASE] User vacation date not found, user_id: %s, user_vacation_date_id: %s",
            user_id,
            user_vacation_date_id,
        )
        raise user_vacation_date_not_found_exception

    for key, value in attrs.items():
        if hasattr(user_vacation_date, key):
            setattr(user_vacation_date, key, value)

    try:
        await session.commit()
    except Exception:
        logger.error(
            "[DATABASE] Failed to update the user vacation date, user_id: %s, user_vacation_date_id: %S",
            user_id,
            user_vacation_date_id,
        )
        raise update_user_vacation_date_exception

    if show_user:

        await session.refresh(user_vacation_date)

        logger.info(
            "[DATABASE] User vacation date has been successfully updated, user_id: %s, user_vacation_date_id: %s and attrs: %s",
            user_id,
            user_vacation_date_id,
            **attrs
        )

        return UserVacationDateSchema.model_validate(
            user_vacation_date, from_attributes=True
        )


async def select_users_vacations_dates(  # type: ignore
    session: AsyncSessionDep, full_info: bool = False, **filters
) -> List[UserVacationDateSchema]:
    users_vacations_dates = await select_users_vacations_dates_instances(
        session=session, full_info=full_info, select_one_instance=False, **filters
    )

    if not users_vacations_dates:
        logger.warning(
            "[DATABASE] Users vacations dates not found, params: %s", **filters
        )
        raise users_vacations_dates_not_found_exception

    logger.info(
        "[DATABASE] Users vacations dates have been successfully selected with params: %s",
        **filters
    )
    validated_users_vacations_dates = [UserVacationDateSchema.model_validate(user_vacation_date, from_attributes=True) for user_vacation_date in users_vacations_dates]  # type: ignore

    return validated_users_vacations_dates


async def delete_user_vacation_date(session: AsyncSessionDep, **filters) -> bool:  # type: ignore
    user_vacation_date = await select_users_vacations_dates_instances(
        session=session, full_info=False, select_one_instance=True, **filters
    )

    if not user_vacation_date:
        logger.warning("[DATABASE] User vacation date not found, params: %s", **filters)
        raise user_vacation_date_not_found_exception

    await session.delete(user_vacation_date)

    logger.info(
        "[DATABASE] User vacation date has been successfully deleted with params: %s",
        **filters
    )

    return True
