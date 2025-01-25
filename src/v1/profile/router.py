import shutil

from fastapi import APIRouter, UploadFile
from fastapi.params import Depends
from starlette.responses import JSONResponse

from src.config import logging_settings
from src.database import AsyncSessionDep
from src.schemas import ProfileSchema, ProfileUpdateSchema
from src.utils import update_profile_with_id
from src.v1.profile.dependencies import get_current_profile_with_user
from src.v1.profile.responses import profile_is_updated_response
from logging import getLogger
from src.container import configure_logging, BASE_DIR

logger = getLogger(__file__)
configure_logging(level=logging_settings.logging_level)

router = APIRouter()


@router.get("/me")
def get_profile(
    profile: ProfileSchema = Depends(get_current_profile_with_user),
) -> JSONResponse:
    return profile


@router.patch("/")
async def update_profile(
    session: AsyncSessionDep,
    profile_update_schema: ProfileUpdateSchema,
    avatar_image_file: UploadFile | None = None,
    profile: ProfileSchema = Depends(get_current_profile_with_user),
) -> JSONResponse:
    profile_update_data = profile_update_schema.model_dump(exclude_none=True)
    if avatar_image_file is not None:
        profile_update_data["avatar"] = avatar_image_file
        logger.info(
            "Image hadn't been sent to update profile's image, profile_id: %s",
            profile.id,
        )
        with open(
            BASE_DIR / f"media/profile/avatar/{avatar_image_file.filename}", "wb"
        ) as file:
            shutil.copyfileobj(avatar_image_file.file, file)
        logger.info(
            "New profile's image was successfully saved on the server, profile_id: %s, image_path: %s",
            profile.id,
            BASE_DIR / f"media/profile/avatar/{avatar_image_file.filename}",
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
