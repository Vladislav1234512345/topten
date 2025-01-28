from typing import List

from fastapi import APIRouter
from fastapi.params import Depends
from starlette.responses import JSONResponse

from src.config import logging_settings
from src.database import AsyncSessionDep
from src.models import UserModel
from src.schemas import UserSchema, UserCreateAndUpdateSchema
from src.utils import (
    create_user,
    select_user,
    update_user_with_id,
    select_users,
    delete_user,
)
from src.exceptions import current_user_yet_exists_exception
from src.v1.jwt.dependencies import get_current_user_with_access_token
from src.v1.jwt.utils import hash_password

from logging import getLogger
from src.container import configure_logging
from src.v1.users.responses import (
    user_is_updated_response,
    user_is_deleted_response,
    user_is_created_response,
)

logger = getLogger(__file__)
configure_logging(level=logging_settings.logging_level)

router = APIRouter()


@router.get("/me")
def get_current_user_view(
    user: UserSchema = Depends(get_current_user_with_access_token),  # type: ignore
) -> UserSchema:
    return user


@router.get("/{user_id}")
async def get_user_view(
    user_id: int,
    session: AsyncSessionDep,
) -> UserSchema:
    return await select_user(session=session, full_info=True, id=user_id)  # type: ignore


@router.get("/")
async def get_users_view(  # type: ignore
    session: AsyncSessionDep,
    **filters,
) -> List[UserSchema]:
    return await select_users(session=session, full_info=False, **filters)  # type: ignore


@router.patch("/")
async def update_user_with_id_view(
    session: AsyncSessionDep,
    user_update_schema: UserCreateAndUpdateSchema,
    user: UserSchema = Depends(get_current_user_with_access_token),  # type: ignore
) -> JSONResponse:
    user_update_data = user_update_schema.model_dump(exclude_none=True)
    if user_update_data.get("password") is not None:
        user_update_data["password"] = hash_password(
            str(user_update_data.get("password"))
        )
    await update_user_with_id(session=session, user_id=user.id, **user_update_data)
    logger.info("User was successfully updated, user_id: %s", user.id)
    return user_is_updated_response


@router.delete("/")
async def delete_current_user_view(
    session: AsyncSessionDep,
    user: UserSchema = Depends(get_current_user_with_access_token),  # type: ignore
) -> JSONResponse:
    await delete_user(session=session, id=user.id)
    logger.info(
        "User was successfully deleted, user_id: %s, phone number: %s",
        user.id,
        user.phone_number,
    )
    return user_is_deleted_response


@router.post("/")
async def create_user_view(
    session: AsyncSessionDep,
    user_create_schema: UserCreateAndUpdateSchema,
) -> JSONResponse:
    user_create_data = user_create_schema.model_dump(exclude_none=True)
    user = await create_user(
        session=session,
        user=UserModel(**user_create_data),
        exception=current_user_yet_exists_exception,
    )
    logger.info(
        "User was successfully created, user_id: %s, phone number: %s",
        user.id,
        user.phone_number,
    )
    return user_is_created_response
