from typing import List

from fastapi import APIRouter
from fastapi.params import Depends
from starlette.responses import JSONResponse

from src.config import logging_settings
from src.database import AsyncSessionDep
from src.models import UserVacationTimeModel
from src.v1.vacations_times.exceptions import (
    current_user_vacation_time_yet_exists_exception,
)
from src.v1.vacations_times.responses import (
    user_vacation_time_is_deleted_response,
    user_vacation_time_is_created_response,
    user_vacation_time_is_updated_response,
)
from src.v1.vacations_times.schemas import (
    UserVacationTimeSchema,
    VacationTimeAndDateBaseSchema,
)
from src.v1.vacations_times.utils import (
    create_user_vacation_time,
    delete_user_vacation_time,
    update_user_vacation_time,
    select_users_vacations_times,
    select_user_vacation_time,
)
from src.v1.users.schemas import UserSchema

from src.v1.jwt.dependencies import get_current_user_with_access_token

from logging import getLogger
from src.container import configure_logging


logger = getLogger(__file__)
configure_logging(level=logging_settings.logging_level)

router = APIRouter()


@router.get("/me")
async def get_current_user_vacations_times_view(
    session: AsyncSessionDep,
    full_info: bool = False,
    user: UserSchema = Depends(get_current_user_with_access_token),  # type: ignore
) -> List[UserVacationTimeSchema]:
    return await select_user_vacation_time(
        session=session, full_info=full_info, user_id=user.id
    )


@router.get("/")
async def get_users_vacations_times_view(  # type: ignore
    session: AsyncSessionDep,
    full_info: bool = False,
    **filters,
) -> List[UserVacationTimeSchema]:
    return await select_users_vacations_times(
        session=session, full_info=full_info, **filters
    )


@router.patch("/{user_vacation_time_id}")
async def update_user_vacation_time_view(
    user_vacation_time_id: int,
    session: AsyncSessionDep,
    vacation_time_and_date_schema: VacationTimeAndDateBaseSchema,
    user: UserSchema = Depends(get_current_user_with_access_token),  # type: ignore
) -> JSONResponse:
    vacation_time_and_date_data = vacation_time_and_date_schema.model_dump(
        exclude_none=True
    )
    await update_user_vacation_time(
        session=session,
        user_vacation_time_id=user_vacation_time_id,
        user_id=user.id,
        **vacation_time_and_date_data,
    )
    logger.info(
        "User vacation time was successfully updated, user_id: %s, user_vacation_time_id: %s",
        user.id,
        user_vacation_time_id,
    )
    return user_vacation_time_is_updated_response


@router.delete("/{user_vacation_time_id}")
async def delete_user_vacation_time_view(
    user_vacation_time_id: int,
    session: AsyncSessionDep,
    user: UserSchema = Depends(get_current_user_with_access_token),  # type: ignore
) -> JSONResponse:
    await delete_user_vacation_time(
        session=session, user_id=user.id, id=user_vacation_time_id
    )
    logger.info(
        "User vacation time was successfully deleted, user_id: %s, user_vacation_time_id: %s",
        user.id,
        user_vacation_time_id,
    )
    return user_vacation_time_is_deleted_response


@router.post("/")
async def create_user_vacation_time_view(
    session: AsyncSessionDep,
    vacation_time_and_date_schema: VacationTimeAndDateBaseSchema,
    user: UserSchema = Depends(get_current_user_with_access_token),  # type: ignore
) -> JSONResponse:
    vacation_time_and_date_data = vacation_time_and_date_schema.model_dump(
        exclude_none=True
    )
    user_vacation_time = await create_user_vacation_time(
        session=session,
        user_vacation_time=UserVacationTimeModel(
            user_id=user.id, **vacation_time_and_date_data
        ),
        exception=current_user_vacation_time_yet_exists_exception,
    )
    logger.info(
        "User vacation time was successfully created, user_id: %s, user_vacation_time_id: %s",
        user.id,
        user_vacation_time.id,
    )
    return user_vacation_time_is_created_response
