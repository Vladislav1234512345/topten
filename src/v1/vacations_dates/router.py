from typing import List

from fastapi import APIRouter
from fastapi.params import Depends
from starlette.responses import JSONResponse

from src.config import logging_settings
from src.database import AsyncSessionDep
from src.models import UserVacationDateModel
from src.v1.vacations_dates.exceptions import (
    current_user_vacation_date_yet_exists_exception,
)
from src.v1.vacations_dates.responses import (
    user_vacation_date_is_deleted_response,
    user_vacation_date_is_created_response,
    user_vacation_date_is_updated_response,
)
from src.v1.vacations_dates.utils import (
    create_user_vacation_date,
    delete_user_vacation_date,
    update_user_vacation_date,
    select_users_vacations_dates,
    select_user_vacation_date,
)
from src.schemas import UserSchema, VacationDateBaseSchema, UserVacationDateSchema

from src.v1.jwt.dependencies import get_current_user_with_access_token

from logging import getLogger
from src.container import configure_logging


logger = getLogger(__file__)
configure_logging(level=logging_settings.logging_level)

router = APIRouter()


@router.get("/me")
async def get_current_user_vacations_dates_view(
    session: AsyncSessionDep,
    full_info: bool = False,
    user: UserSchema = Depends(get_current_user_with_access_token),  # type: ignore
) -> List[UserVacationDateSchema]:
    return await select_user_vacation_date(  # type: ignore
        session=session, full_info=full_info, user_id=user.id
    )


@router.get("/")
async def get_users_vacations_dates_view(  # type: ignore
    session: AsyncSessionDep,
    full_info: bool = False,
    **filters,
) -> List[UserVacationDateSchema]:
    return await select_users_vacations_dates(
        session=session, full_info=full_info, **filters
    )


@router.put("/{user_vacation_date_id}")
async def update_user_vacation_date_view(
    user_vacation_date_id: int,
    session: AsyncSessionDep,
    vacation_date_schema: VacationDateBaseSchema,
    user: UserSchema = Depends(get_current_user_with_access_token),  # type: ignore
) -> JSONResponse:
    vacation_date_data = vacation_date_schema.model_dump(exclude_none=True)
    await update_user_vacation_date(
        session=session,
        user_vacation_date_id=user_vacation_date_id,
        user_id=user.id,
        **vacation_date_data,
    )
    logger.info(
        "User vacation date was successfully updated, user_id: %s, user_vacation_date_id: %s",
        user.id,
        user_vacation_date_id,
    )
    return user_vacation_date_is_updated_response


@router.delete("/{user_vacation_date_id}")
async def delete_user_vacation_date_view(
    user_vacation_date_id: int,
    session: AsyncSessionDep,
    user: UserSchema = Depends(get_current_user_with_access_token),  # type: ignore
) -> JSONResponse:
    await delete_user_vacation_date(
        session=session, user_id=user.id, id=user_vacation_date_id
    )
    logger.info(
        "User vacation date was successfully deleted, user_id: %s, user_vacation_date_id: %s",
        user.id,
        user_vacation_date_id,
    )
    return user_vacation_date_is_deleted_response


@router.post("/")
async def create_user_vacation_date_view(
    session: AsyncSessionDep,
    vacation_date_schema: VacationDateBaseSchema,
    user: UserSchema = Depends(get_current_user_with_access_token),  # type: ignore
) -> JSONResponse:
    vacation_date_data = vacation_date_schema.model_dump(exclude_none=True)
    user_vacation_date = await create_user_vacation_date(
        session=session,
        user_vacation_date=UserVacationDateModel(user_id=user.id, **vacation_date_data),
        exception=current_user_vacation_date_yet_exists_exception,
    )
    logger.info(
        "User vacation date was successfully created, user_id: %s, user_vacation_date_id: %s",
        user.id,
        user_vacation_date.id,
    )
    return user_vacation_date_is_created_response
