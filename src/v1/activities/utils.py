from typing import List

from starlette.exceptions import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from src.database import AsyncSessionDep
from src.v1.activities.exceptions import (
    activities_not_found_exception,
    activity_not_found_exception,
    update_activity_exception,
)
from src.v1.activities.schemas import ActivitySchema
from src.models import ActivityModel
import logging
from src.container import configure_logging
from src.config import logging_settings


logger = logging.getLogger(__name__)
configure_logging(level=logging_settings.logging_level)


async def create_activity(
    activity: ActivityModel, session: AsyncSessionDep, exception: HTTPException
) -> ActivitySchema:
    session.add(activity)
    try:
        await session.commit()
    except Exception:
        logger.warning(
            "[DATABASE] Current activity has been existed yet, name %s",
            activity.name,
        )
        raise exception
    await session.refresh(activity)
    logger.info(
        "[DATABASE] Activity has been successfully created, activity_id: %s, name: %s",
        activity.id,
        activity.name,
    )
    return ActivitySchema.model_validate(activity, from_attributes=True)


async def select_activities_instances(session: AsyncSessionDep, select_one_instance: bool = True, full_info: bool = True, **filters) -> ActivityModel | List[ActivityModel] | None:  # type: ignore
    statement = select(ActivityModel).filter_by(**filters)
    if full_info:
        statement.options(
            selectinload(ActivityModel.users),
            selectinload(ActivityModel.cards),
        )
    try:
        result = await session.execute(statement)
        if select_one_instance:
            return result.scalar()
        else:
            return list(result.scalars().all())
    except:
        if select_one_instance:
            logger.warning("[DATABASE] Activity not found, params: %s", **filters)
            raise activity_not_found_exception
        else:
            logger.warning("[DATABASE] Activities not found, params: %s", **filters)
            raise activities_not_found_exception


async def select_activity(  # type: ignore
    session: AsyncSessionDep, full_info: bool = False, **filters
) -> ActivitySchema:
    activity = await select_activities_instances(
        session=session, select_one_instance=True, full_info=full_info, **filters
    )

    if not activity:
        logger.warning("[DATABASE] Activity not found, params: %s", **filters)
        raise activity_not_found_exception

    logger.info(
        "[DATABASE] Activity has been successfully selected, activity_id: %s, name: %s",
        activity.id,  # type: ignore
        activity.name,  # type: ignore
    )
    return ActivitySchema.model_validate(activity, from_attributes=True)


async def update_activity(  # type: ignore
    session: AsyncSessionDep, activity_id: int, show_user: bool = False, **attrs
) -> ActivitySchema:
    activity = await select_activities_instances(
        session=session, select_one_instance=True, full_info=False, id=activity_id
    )
    if not activity:
        logger.warning("[DATABASE] Activity not found, activity_id: %s", activity_id)
        raise activity_not_found_exception

    for key, value in attrs.items():
        if hasattr(activity, key):
            setattr(activity, key, value)

    try:
        await session.commit()
    except Exception:
        logger.error(
            "[DATABASE] Failed to update the activity, activity_id: %s", activity_id
        )
        raise update_activity_exception

    if show_user:

        await session.refresh(activity)

        logger.info(
            "[DATABASE] Activity has been successfully updated, activity_id: %s and attrs: %s",
            activity_id,
            **attrs
        )

        return ActivitySchema.model_validate(activity, from_attributes=True)


async def select_activities(  # type: ignore
    session: AsyncSessionDep, full_info: bool = False, **filters
) -> List[ActivitySchema]:
    activities = await select_activities_instances(
        session=session, full_info=full_info, select_one_instance=False, **filters
    )

    if not activities:
        logger.warning("[DATABASE] Activities not found, params: %s", **filters)
        raise activities_not_found_exception

    logger.info(
        "[DATABASE] Activities have been successfully selected with params: %s",
        **filters
    )
    validated_activities = [ActivitySchema.model_validate(activity, from_attributes=True) for activity in activities]  # type: ignore

    return validated_activities


async def delete_activity(session: AsyncSessionDep, **filters) -> bool:  # type: ignore
    activity = await select_activities_instances(
        session=session, full_info=False, select_one_instance=True, **filters
    )

    if not activity:
        logger.warning("[DATABASE] Activity not found, params: %s", **filters)
        raise activity_not_found_exception

    await session.delete(activity)

    logger.info(
        "[DATABASE] Activity has been successfully deleted with params: %s", **filters
    )

    return True
