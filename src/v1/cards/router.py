import shutil
from typing import List

from fastapi import APIRouter
from fastapi.params import Depends
from starlette.datastructures import UploadFile
from starlette.responses import JSONResponse

from src.config import logging_settings, web_settings
from src.database import AsyncSessionDep
from src.models import UserCardModel
from src.v1.cards.schemas import (
    UserCardCreateSchema,
    UserCardUpdateSchema,
    UserCardSchema,
)
from src.v1.users.schemas import UserSchema
from src.v1.cards.utils import (
    create_user_card,
    delete_user_card,
    select_user_card,
    update_user_card_with_user_and_activity_ids,
    select_users_cards,
)
from src.v1.cards.exceptions import current_user_card_yet_exists_exception
from src.v1.jwt.dependencies import get_current_user_with_access_token

from logging import getLogger
from src.container import configure_logging, BASE_DIR
from src.v1.cards.responses import (
    user_card_is_created_response,
    user_card_is_deleted_response,
    user_card_is_updated_response,
)

logger = getLogger(__file__)
configure_logging(level=logging_settings.logging_level)

router = APIRouter()


@router.get("/me")
async def get_current_user_cards_view(
    session: AsyncSessionDep,
    full_info: bool = True,
    user: UserSchema = Depends(get_current_user_with_access_token),  # type: ignore
) -> List[UserCardSchema]:
    return await select_users_cards(
        session=session, full_info=full_info, user_id=user.id
    )


@router.get("/{user_card_id}")
async def get_user_card_view(
    user_card_id: int,
    session: AsyncSessionDep,
    full_info: bool = True,
) -> UserCardSchema:
    return await select_user_card(session=session, full_info=full_info, id=user_card_id)


@router.get("/")
async def get_users_cards_view(  # type: ignore
    session: AsyncSessionDep,
    full_info: bool = False,
    **filters,
) -> List[UserCardSchema]:
    return await select_users_cards(session=session, full_info=full_info, **filters)


@router.patch("/")
async def update_user_card_with_user_and_activity_ids_view(
    session: AsyncSessionDep,
    user_card_update_schema: UserCardUpdateSchema,
    card_image_file: UploadFile | None = None,
    user: UserSchema = Depends(get_current_user_with_access_token),  # type: ignore
) -> JSONResponse:
    user_card_update_data = user_card_update_schema.model_dump(exclude_none=True)

    if card_image_file is not None:
        card_image_file_path = f"/media/images/cards/{card_image_file.filename}"
        logger.info(
            "Image hadn't been sent to update the user card's image, user_id: %s, activity_id: %s",
            user.id,
            user_card_update_schema.activity_id,
        )
        with open(BASE_DIR / card_image_file_path, "wb") as file:
            shutil.copyfileobj(card_image_file.file, file)
        logger.info(
            "New user card's image was successfully saved on the server, user_id: %s, image_path: %s",
            user.id,
            BASE_DIR / card_image_file_path,
        )
        user_card_update_data["card_image"] = (
            web_settings.BACKEND_LINK + card_image_file_path
        )

    logger.info(
        "Image had been sent to update the current user card's image, user_id: %s, activity_id: %s",
        user.id,
        user_card_update_schema.activity_id,
    )

    await update_user_card_with_user_and_activity_ids(
        session=session,
        user_id=user.id,
        activity_id=user_card_update_schema.activity_id,
        **user_card_update_data,
    )

    logger.info(
        "User Card was successfully updated, user_id: %s, activity_id: %s",
        user.id,
        user_card_update_schema.activity_id,
    )

    return user_card_is_updated_response


@router.delete("/{user_card_id}")
async def delete_user_card_view(
    user_card_id: int,
    session: AsyncSessionDep,
    user: UserSchema = Depends(get_current_user_with_access_token),  # type: ignore
) -> JSONResponse:
    await delete_user_card(session=session, id=user_card_id, user_id=user.id)
    logger.info(
        "User Card was successfully deleted, user_id: %s, user_card_id: %s",
        user.id,
        user_card_id,
    )
    return user_card_is_deleted_response


@router.post("/")
async def create_user_card_view(
    session: AsyncSessionDep,
    user_card_create_schema: UserCardCreateSchema,
    card_image_file: UploadFile | None = None,
    user: UserSchema = Depends(get_current_user_with_access_token),  # type: ignore
) -> JSONResponse:
    user_card_create_data = user_card_create_schema.model_dump(exclude_none=True)

    if card_image_file is not None:
        card_image_file_path = f"/media/images/cards/{card_image_file.filename}"
        logger.info(
            "Image hadn't been sent to create the user card, user_id: %s, activity_id: %s",
            user.id,
            user_card_create_schema.activity_id,
        )
        with open(BASE_DIR / card_image_file_path, "wb") as file:
            shutil.copyfileobj(card_image_file.file, file)
        logger.info(
            "Card's image was successfully saved on the server, user_id: %s, activity_id: %s, image_path: %s",
            user.id,
            user_card_create_schema.activity_id,
            BASE_DIR / card_image_file_path,
        )
        user_card_create_data["card_image"] = (
            web_settings.BACKEND_LINK + card_image_file_path
        )

    logger.info(
        "Image had been sent to create the current user card, user_id: %s",
        user.id,
    )

    user_card = await create_user_card(
        session=session,
        user_card=UserCardModel(user_id=user.id, **user_card_create_data),
        exception=current_user_card_yet_exists_exception,
    )

    logger.info(
        "User Card was successfully created, user_card_id: %s, user_card_id: %s, phone number: %s",
        user.id,
        user_card.id,
        user.phone_number,
    )

    return user_card_is_created_response
