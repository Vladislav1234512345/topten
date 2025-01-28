from typing import List

from fastapi import APIRouter
from fastapi.params import Depends
from starlette.responses import JSONResponse

from src.config import logging_settings
from src.database import AsyncSessionDep
from src.models import UserWeekDayModel
from src.v1.week_days.exceptions import current_user_week_day_yet_exists_exception
from src.v1.week_days.responses import (
    user_week_day_is_deleted_response,
    user_week_day_is_created_response,
    user_week_day_is_updated_response,
)
from src.v1.week_days.schemas import (
    WeekDayBaseSchema,
    WorkTimeBaseSchema,
    UserWeekDaySchema,
    WeekDaySchema,
)
from src.v1.week_days.utils import (
    create_user_week_day,
    delete_user_week_day,
    update_user_week_day,
    select_users_week_days,
    select_user_week_day,
)
from src.v1.users.schemas import UserSchema

from src.v1.jwt.dependencies import get_current_user_with_access_token

from logging import getLogger
from src.container import configure_logging


logger = getLogger(__file__)
configure_logging(level=logging_settings.logging_level)

router = APIRouter()


@router.get("/me")
async def get_current_user_week_days_view(
    session: AsyncSessionDep,
    full_info: bool = False,
    user: UserSchema = Depends(get_current_user_with_access_token),  # type: ignore
) -> List[UserWeekDaySchema]:
    return await select_user_week_day(  # type: ignore
        session=session, full_info=full_info, user_id=user.id
    )


@router.get("/{user_id}")
async def get_user_week_day_view(
    user_id: int,
    session: AsyncSessionDep,
    full_info: bool = False,
) -> UserWeekDaySchema:
    return await select_user_week_day(
        session=session, full_info=full_info, user_id=user_id
    )


@router.get("/")
async def get_users_week_days_view(  # type: ignore
    session: AsyncSessionDep,
    full_info: bool = False,
    **filters,
) -> List[UserWeekDaySchema]:
    return await select_users_week_days(session=session, full_info=full_info, **filters)


@router.patch("/")
async def update_user_week_day_view(
    session: AsyncSessionDep,
    week_day_base_schema: WeekDayBaseSchema,
    work_time_schema: WorkTimeBaseSchema,
    user: UserSchema = Depends(get_current_user_with_access_token),  # type: ignore
) -> JSONResponse:
    work_time_data = work_time_schema.model_dump(exclude_none=True)
    await update_user_week_day(
        session=session,
        week_day=week_day_base_schema.week_day,
        user_id=user.id,
        **work_time_data,
    )
    logger.info(
        "User week day was successfully updated, user_id: %s, week_day: %s",
        user.id,
        week_day_base_schema.week_day,
    )
    return user_week_day_is_updated_response


@router.delete("/")
async def delete_user_week_day_view(
    week_day: WeekDayBaseSchema,
    session: AsyncSessionDep,
    user: UserSchema = Depends(get_current_user_with_access_token),  # type: ignore
) -> JSONResponse:
    await delete_user_week_day(session=session, user_id=user.id, week_day=week_day)
    logger.info(
        "User week day was successfully deleted, user_id: %s, week_day: %s",
        user.id,
        week_day,
    )
    return user_week_day_is_deleted_response


@router.post("/")
async def create_user_week_day_view(
    session: AsyncSessionDep,
    week_day_schema: WeekDaySchema,
    user: UserSchema = Depends(get_current_user_with_access_token),  # type: ignore
) -> JSONResponse:
    week_day_and_work_time_data = week_day_schema.model_dump(exclude_none=True)
    user_week_day = await create_user_week_day(
        session=session,
        user_week_day=UserWeekDayModel(user_id=user.id, **week_day_and_work_time_data),
        exception=current_user_week_day_yet_exists_exception,
    )
    logger.info(
        "User week days was successfully created, user_id: %s, user_week_day_id: %s, week_day: %s",
        user.id,
        user_week_day.id,
        user_week_day.week_day,
    )
    return user_week_day_is_created_response
