import shutil
from typing import List

from fastapi import APIRouter
from fastapi.params import Depends
from starlette.datastructures import UploadFile
from starlette.responses import JSONResponse

from src.config import logging_settings, web_settings
from src.database import AsyncSessionDep
from src.models import UserCardModel, UserCardReviewModel
from src.v1.reviews.exceptions import current_user_card_review_yet_exists_exception
from src.v1.reviews.responses import (
    user_card_review_is_created_response,
    user_card_review_is_deleted_response,
    user_card_review_is_updated_response,
)
from src.v1.reviews.schemas import (
    UserCardReviewBaseSchema,
    UserCardReviewUpdateSchema,
    UserCardReviewSchema,
)
from src.v1.users.schemas import UserSchema
from src.v1.reviews.utils import (
    create_user_card_review,
    delete_user_card_review,
    select_user_card_review,
    update_user_card_review,
    select_users_cards_reviews,
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
async def get_current_user_cards_reviews_view(
    session: AsyncSessionDep,
    full_info: bool = True,
    user: UserSchema = Depends(get_current_user_with_access_token),  # type: ignore
) -> List[UserCardReviewSchema]:
    return await select_users_cards_reviews(
        session=session, full_info=full_info, user_id=user.id
    )


@router.get("/user_id{user_id}")
async def get_users_cards_reviews_with_user_id_view(
    user_id: int,
    session: AsyncSessionDep,
    full_info: bool = False,
) -> List[UserCardReviewSchema]:
    return await select_users_cards_reviews(
        session=session, full_info=full_info, user_id=user_id
    )


@router.get("/user_card_id{user_card_id}")
async def get_users_cards_reviews_with_user_card_id_view(
    user_card_id: int,
    session: AsyncSessionDep,
    full_info: bool = False,
) -> List[UserCardReviewSchema]:
    return await select_users_cards_reviews(
        session=session, full_info=full_info, user_card_id=user_card_id
    )


@router.get("/")
async def get_users_cards_reviews_view(  # type: ignore
    session: AsyncSessionDep,
    full_info: bool = False,
    **filters,
) -> List[UserCardReviewSchema]:
    return await select_users_cards_reviews(
        session=session, full_info=full_info, **filters
    )


@router.patch("/{user_card_id}")
async def update_user_card_review_view(
    user_card_id: int,
    session: AsyncSessionDep,
    user_card_review_update_schema: UserCardReviewUpdateSchema,
    user: UserSchema = Depends(get_current_user_with_access_token),  # type: ignore
) -> JSONResponse:
    user_card_review_update_data = user_card_review_update_schema.model_dump(
        exclude_none=True
    )

    await update_user_card_review(
        session=session,
        user_id=user.id,
        user_card_id=user_card_id,
        **user_card_review_update_data,
    )

    logger.info(
        "User Card Review was successfully updated, user_id: %s, user_card_id: %s",
        user.id,
        user_card_id,
    )

    return user_card_review_is_updated_response


@router.delete("/{user_card_id}")
async def delete_user_card_review_view(
    user_card_id: int,
    session: AsyncSessionDep,
    user: UserSchema = Depends(get_current_user_with_access_token),  # type: ignore
) -> JSONResponse:
    await delete_user_card_review(
        session=session, user_card_id=user_card_id, user_id=user.id
    )
    logger.info(
        "User Card Review was successfully deleted, user_id: %s, user_card_id: %s",
        user.id,
        user_card_id,
    )
    return user_card_review_is_deleted_response


@router.post("/")
async def create_user_card_review_view(
    session: AsyncSessionDep,
    user_card_review_base_schema: UserCardReviewBaseSchema,
    user: UserSchema = Depends(get_current_user_with_access_token),  # type: ignore
) -> JSONResponse:
    user_card_review_base_data = user_card_review_base_schema.model_dump(
        exclude_none=True
    )
    user_card_review = await create_user_card_review(
        session=session,
        user_card_review=UserCardReviewModel(
            user_id=user.id, **user_card_review_base_data
        ),
        exception=current_user_card_review_yet_exists_exception,
    )

    logger.info(
        "User Card Review was successfully created, user_id: %s, user_card_id: %s",
        user.id,
        user_card_review.user_card_id,
    )

    return user_card_review_is_created_response
