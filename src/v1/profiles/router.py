import shutil
from typing import List

from fastapi import APIRouter, UploadFile
from fastapi.params import Depends
from starlette.responses import JSONResponse

from src.config import logging_settings, web_settings
from src.database import AsyncSessionDep
from src.models import ProfileModel
from src.schemas import ProfileSchema, UserSchema, ProfileCreateAndUpdateSchema
from src.v1.profiles.utils import (
    delete_profile,
    create_profile,
    select_profile,
    update_profile_with_id,
    select_profiles,
)
from src.v1.auth.exceptions import current_profile_yet_exists_exception
from src.v1.jwt.dependencies import get_current_user_with_access_token
from src.v1.profiles.dependencies import get_current_profile_with_user
from src.v1.profiles.responses import (
    profile_is_updated_response,
    profile_is_deleted_response,
    profile_is_created_response,
)
from logging import getLogger
from src.container import configure_logging, BASE_DIR

logger = getLogger(__file__)
configure_logging(level=logging_settings.logging_level)

router = APIRouter()


@router.get("/me")
def get_current_profile_view(
    profile: ProfileSchema = Depends(get_current_profile_with_user),  # type: ignore
) -> ProfileSchema:
    return profile


@router.get("/{profile_id}")
async def get_profile_view(
    profile_id: int,
    session: AsyncSessionDep,
) -> ProfileSchema:
    return await select_profile(session=session, id=profile_id)


@router.get("/")
async def get_profiles_view(  # type: ignore
    session: AsyncSessionDep,
    **filters,
) -> List[ProfileSchema]:
    return await select_profiles(session=session, **filters)


@router.patch("/")
async def update_profile_view(
    session: AsyncSessionDep,
    profile_update_schema: ProfileCreateAndUpdateSchema,
    avatar_image_file: UploadFile | None = None,
    profile: ProfileSchema = Depends(get_current_profile_with_user),  # type: ignore
) -> JSONResponse:
    profile_update_data = profile_update_schema.model_dump(exclude_none=True)
    if avatar_image_file is not None:
        avatar_image_file_path = f"/media/images/profiles/{avatar_image_file.filename}"
        logger.info(
            "Image hadn't been sent to update the profile's image, profile_id: %s",
            profile.id,
        )
        with open(BASE_DIR / avatar_image_file_path, "wb") as file:
            shutil.copyfileobj(avatar_image_file.file, file)
        logger.info(
            "New profile's image was successfully saved on the server, profile_id: %s, image_path: %s",
            profile.id,
            BASE_DIR / avatar_image_file_path,
        )
        profile_update_data["avatar"] = (
            web_settings.BACKEND_LINK + avatar_image_file_path
        )

    logger.info(
        "Image had been sent to update current profile's image, profile_id: %s",
        profile.id,
    )
    await update_profile_with_id(
        session=session, profile_id=profile.id, **profile_update_data
    )
    logger.info("Profile was successfully updated, profile_id: %s", profile.id)
    return profile_is_updated_response


@router.delete("/")
async def delete_current_profile_view(
    session: AsyncSessionDep,
    profile: ProfileSchema = Depends(get_current_profile_with_user),  # type: ignore
) -> JSONResponse:
    await delete_profile(session=session, id=profile.id)
    logger.info(
        "Profile was successfully deleted, user_id: %s, profile_id: %s",
        profile.user_id,
        profile.id,
    )
    return profile_is_deleted_response


@router.post("/")
async def create_profile_view(
    session: AsyncSessionDep,
    profile_create_schema: ProfileCreateAndUpdateSchema,
    avatar_image_file: UploadFile | None = None,
    user: UserSchema = Depends(get_current_user_with_access_token),  # type: ignore
) -> JSONResponse:
    profile_create_data = profile_create_schema.model_dump(exclude_none=True)
    if avatar_image_file is not None:
        avatar_image_file_path = f"/media/images/profiles/{avatar_image_file.filename}"
        logger.info(
            "Image hadn't been sent to create the profile, user_id: %s",
            user.id,
        )
        with open(BASE_DIR / avatar_image_file_path, "wb") as file:
            shutil.copyfileobj(avatar_image_file.file, file)
        logger.info(
            "Profile's image was successfully saved on the server, user_id: %s, image_path: %s",
            user.id,
            BASE_DIR / avatar_image_file_path,
        )
        profile_create_data["avatar"] = (
            web_settings.BACKEND_LINK + avatar_image_file_path
        )

    logger.info(
        "Image had been sent to create the current profile, user_id: %s",
        user.id,
    )
    profile = await create_profile(
        session=session,
        profile=ProfileModel(user_id=user.id, **profile_create_data),
        exception=current_profile_yet_exists_exception,
    )
    logger.info(
        "Profile was successfully created, profile_id: %s, user_id: %s, phone number: %s",
        profile.id,
        user.id,
        user.phone_number,
    )
    return profile_is_created_response
