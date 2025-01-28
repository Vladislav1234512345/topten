from typing import List

from fastapi import APIRouter
from fastapi.params import Depends
from starlette.responses import JSONResponse

from src.config import logging_settings
from src.database import AsyncSessionDep
from src.models import ActivityModel
from src.v1.activities.exceptions import current_activity_yet_exists_exception
from src.v1.activities.responses import (
    activity_is_deleted_response,
    activity_is_created_response,
    activity_is_updated_response,
)
from src.schemas import ActivitySchema, UserSchema, ActivityBaseSchema
from src.v1.activities.utils import (
    create_activity,
    delete_activity,
    update_activity,
    select_activities,
    select_activity,
)

from src.v1.jwt.dependencies import (
    get_current_user_with_access_token,
    get_current_admin_role_and_higher_permission_with_access_token,
)

from logging import getLogger
from src.container import configure_logging


logger = getLogger(__file__)
configure_logging(level=logging_settings.logging_level)

router = APIRouter()


@router.get("/me")
async def get_current_user_activities(
    session: AsyncSessionDep,
    user: UserSchema = Depends(get_current_user_with_access_token),  # type: ignore
) -> List[ActivitySchema]:
    return await select_activities(session=session, full_info=True, id=user.id)


@router.get("/{activity_id}")
async def get_activity_view(
    activity_id: int,
    session: AsyncSessionDep,
) -> ActivitySchema:
    return await select_activity(session=session, full_info=True, id=activity_id)


@router.get("/")
async def get_activities_view(  # type: ignore
    session: AsyncSessionDep,
    **filters,
) -> List[ActivitySchema]:
    return await select_activities(session=session, full_info=False, **filters)


@router.patch("/{activity_id}")
async def update_activity_view(
    activity_id: int,
    session: AsyncSessionDep,
    activity_base_schema: ActivityBaseSchema,
    user: UserSchema = Depends(  # type: ignore
        get_current_admin_role_and_higher_permission_with_access_token
    ),
) -> JSONResponse:
    activity_update_data = activity_base_schema.model_dump(exclude_none=True)
    await update_activity(session=session, id=activity_id, **activity_update_data)
    logger.info(
        "Activity was successfully updated, user_id: %s, user phone number: %s, activity_id: %s, activity name: %s",
        user.id,
        user.phone_number,
        activity_id,
        activity_base_schema.name,
    )
    return activity_is_updated_response


@router.delete("/{activity_id}")
async def delete_activity_view(
    activity_id: int,
    session: AsyncSessionDep,
    user: UserSchema = Depends(  # type: ignore
        get_current_admin_role_and_higher_permission_with_access_token
    ),
) -> JSONResponse:
    await delete_activity(session=session, id=activity_id)
    logger.info(
        "Activity was successfully deleted, user_id: %s, user phone number: %s, activity_id: %s",
        user.id,
        user.phone_number,
        activity_id,
    )
    return activity_is_deleted_response


@router.post("/")
async def create_activity_view(
    session: AsyncSessionDep,
    activity_schema: ActivityBaseSchema,
    user: UserSchema = Depends(  # type: ignore
        get_current_admin_role_and_higher_permission_with_access_token
    ),
) -> JSONResponse:
    activity_data = activity_schema.model_dump(exclude_none=True)
    activity = await create_activity(
        session=session,
        activity=ActivityModel(**activity_data),
        exception=current_activity_yet_exists_exception,
    )
    logger.info(
        "Activity was successfully created, user_id: %s, user phone number: %s, activity_id: %s, activity name: %s",
        user.id,
        user.phone_number,
        activity.id,
        activity.name,
    )
    return activity_is_created_response
