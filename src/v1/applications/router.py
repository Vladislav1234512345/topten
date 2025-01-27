from typing import List

from fastapi import APIRouter
from fastapi.params import Depends
from starlette.responses import JSONResponse

from src.config import logging_settings
from src.database import AsyncSessionDep
from src.models import ApplicationModel
from src.v1.applications.schemas import (
    ApplicationUpdateSchema,
    ApplicationSchema,
    ApplicationBaseSchema,
)
from src.v1.users.schemas import UserSchema
from src.v1.applications.utils import (
    create_application,
    delete_application,
    select_application,
    update_application,
    select_applications,
)
from src.v1.applications.exceptions import current_application_yet_exists_exception
from src.v1.jwt.dependencies import get_current_user_with_access_token

from logging import getLogger
from src.container import configure_logging
from src.v1.applications.responses import (
    application_is_created_response,
    application_is_deleted_response,
    application_is_updated_response,
)

logger = getLogger(__file__)
configure_logging(level=logging_settings.logging_level)

router = APIRouter()


@router.get("/me")
async def get_current_user_applications_view(
    session: AsyncSessionDep,
    full_info: bool = True,
    user: UserSchema = Depends(get_current_user_with_access_token),  # type: ignore
) -> List[ApplicationSchema]:
    return await select_applications(
        session=session, full_info=full_info, user_id=user.id
    )


@router.get("/{application_id}")
async def get_application_view(
    application_id: int,
    session: AsyncSessionDep,
    full_info: bool = True,
) -> ApplicationSchema:
    return await select_application(
        session=session, full_info=full_info, id=application_id
    )


@router.get("/")
async def get_applications_view(  # type: ignore
    session: AsyncSessionDep,
    full_info: bool = False,
    **filters,
) -> List[ApplicationSchema]:
    return await select_applications(session=session, full_info=full_info, **filters)


@router.patch("/{application_id}")
async def update_application_view(
    application_id: int,
    session: AsyncSessionDep,
    application_update_schema: ApplicationUpdateSchema,
    user: UserSchema = Depends(get_current_user_with_access_token),  # type: ignore
) -> JSONResponse:
    application_update_data = application_update_schema.model_dump(exclude_none=True)

    await update_application(
        session=session,
        current_user_id=user.id,
        application_id=application_id,
        **application_update_data,
    )

    logger.info(
        "Application was successfully updated, user_id: %s, application_id: %s",
        user.id,
        application_id,
    )

    return application_is_updated_response


@router.delete("/{application_id}")
async def delete_application_view(
    application_id: int,
    session: AsyncSessionDep,
    user: UserSchema = Depends(get_current_user_with_access_token),  # type: ignore
) -> JSONResponse:
    await delete_application(session=session, id=application_id, user_id=user.id)
    logger.info(
        "Application was successfully deleted, user_id: %s, application_id: %s",
        user.id,
        application_id,
    )
    return application_is_deleted_response


@router.post("/")
async def create_application_view(
    session: AsyncSessionDep,
    application_base_schema: ApplicationBaseSchema,
    user: UserSchema = Depends(get_current_user_with_access_token),  # type: ignore
) -> JSONResponse:
    application_create_data = application_base_schema.model_dump(exclude_none=True)

    application = await create_application(
        session=session,
        application=ApplicationModel(user_id=user.id, **application_create_data),
        exception=current_application_yet_exists_exception,
    )

    logger.info(
        "Application was successfully created, user_id: %s, application_id: %s, user_card_service_id: %s",
        user.id,
        application.id,
        application.user_card_service_id,
    )

    return application_is_created_response
