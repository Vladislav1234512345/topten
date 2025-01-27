from typing import List

from fastapi import APIRouter
from fastapi.params import Depends
from starlette.responses import JSONResponse

from src.config import logging_settings
from src.database import AsyncSessionDep
from src.models import ActivityModel, UserBreakModel
from src.v1.breaks.exceptions import current_user_break_yet_exists_exception
from src.v1.breaks.responses import (
    user_break_is_deleted_response,
    user_break_is_created_response,
    user_break_is_updated_response,
)
from src.v1.breaks.schemas import UserBreakBaseSchema, UserBreakSchema
from src.v1.breaks.utils import (
    create_user_break,
    delete_user_break,
    update_user_break,
    select_users_breaks,
    select_user_break,
)
from src.v1.users.schemas import UserSchema

from src.v1.jwt.dependencies import (
    get_current_user_with_access_token,
)

from logging import getLogger
from src.container import configure_logging


logger = getLogger(__file__)
configure_logging(level=logging_settings.logging_level)

router = APIRouter()


@router.get("/me")
async def get_current_user_break_view(
    session: AsyncSessionDep,
    full_info: bool = False,
    user: UserSchema = Depends(get_current_user_with_access_token),  # type: ignore
) -> List[UserBreakSchema]:
    return await select_user_break(session=session, full_info=full_info, id=user.id)


@router.get("/{user_id}")
async def get_user_break_view(
    user_id: int,
    session: AsyncSessionDep,
    full_info: bool = False,
) -> UserBreakSchema:
    return await select_user_break(
        session=session, full_info=full_info, user_id=user_id
    )


@router.get("/")
async def get_users_breaks_view(  # type: ignore
    session: AsyncSessionDep,
    full_info: bool = False,
    **filters,
) -> List[UserBreakSchema]:
    return await select_users_breaks(session=session, full_info=full_info, **filters)


@router.patch("/")
async def update_user_break_view(
    session: AsyncSessionDep,
    user_break_base_schema: UserBreakBaseSchema,
    user: UserSchema = Depends(get_current_user_with_access_token),  # type: ignore
) -> JSONResponse:
    user_break_update_data = user_break_base_schema.model_dump(exclude_none=True)
    await update_user_break(session=session, user_id=user.id, **user_break_update_data)
    logger.info(
        "User break was successfully updated, user_id: %s, user_break time: %s",
        user.id,
        user_break_base_schema.break_time,
    )
    return user_break_is_updated_response


@router.delete("/")
async def delete_user_break_view(
    session: AsyncSessionDep,
    user: UserSchema = Depends(get_current_user_with_access_token),  # type: ignore
) -> JSONResponse:
    await delete_user_break(session=session, user_id=user.id)
    logger.info(
        "Activity was successfully deleted, user_id: %s",
        user.id,
    )
    return user_break_is_deleted_response


@router.post("/")
async def create_activity_view(
    session: AsyncSessionDep,
    user_break_base_schema: UserBreakBaseSchema,
    user: UserSchema = Depends(get_current_user_with_access_token),  # type: ignore
) -> JSONResponse:
    user_break_data = user_break_base_schema.model_dump(exclude_none=True)
    user_break = await create_user_break(
        session=session,
        user_break=UserBreakModel(**user_break_data),
        exception=current_user_break_yet_exists_exception,
    )
    logger.info(
        "User break was successfully created, user_id: %s, user_break_id: %s, user_break time: %s",
        user.id,
        user_break.id,
        user_break.break_time,
    )
    return user_break_is_created_response
