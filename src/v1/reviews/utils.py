from typing import List

from starlette.exceptions import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from src.database import AsyncSessionDep
from src.v1.reviews.exceptions import (
    update_user_card_review_exception,
)

from src.v1.reviews.exceptions import (
    users_cards_reviews_not_found_exception,
    user_card_review_not_found_exception,
)
from src.models import UserCardReviewModel
from src.v1.reviews.schemas import UserCardReviewSchema
import logging
from src.container import configure_logging
from src.config import logging_settings


logger = logging.getLogger(__name__)
configure_logging(level=logging_settings.logging_level)


async def create_user_card_review(
    user_card_review: UserCardReviewModel,
    session: AsyncSessionDep,
    exception: HTTPException,
) -> UserCardReviewSchema:
    session.add(user_card_review)
    try:
        await session.commit()
    except Exception:
        logger.warning(
            "[DATABASE] Current user card review has been existed yet, user_id: %s, user_card_id: %s",
            user_card_review.user_id,
            user_card_review.user_card_id,
        )
        raise exception
    await session.refresh(user_card_review)
    logger.info(
        "[DATABASE] User Card Review has been successfully created, user_id: %s, user_card_id: %s",
        user_card_review.user_id,
        user_card_review.user_card_id,
    )
    return UserCardReviewSchema.model_validate(user_card_review, from_attributes=True)


async def select_users_cards_reviews_instances(session: AsyncSessionDep, select_one_instance: bool = True, full_info: bool = True, **filters) -> UserCardReviewModel | List[UserCardReviewModel] | None:  # type: ignore
    statement = select(UserCardReviewModel).filter_by(**filters)
    if full_info:
        statement.options(
            joinedload(UserCardReviewModel.card),
            joinedload(UserCardReviewModel.user_sender),
        )
    try:
        result = await session.execute(statement)
        if select_one_instance:
            return result.scalar()
        else:
            return list(result.scalars().all())
    except:
        if select_one_instance:
            logger.warning(
                "[DATABASE] User Card Review not found, params: %s", **filters
            )
            raise user_card_review_not_found_exception
        else:
            logger.warning(
                "[DATABASE] Users Cards Reviews not found, params: %s", **filters
            )
            raise users_cards_reviews_not_found_exception


async def select_user_card_review(  # type: ignore
    session: AsyncSessionDep, full_info: bool = False, **filters
) -> UserCardReviewSchema:
    user_card_review = await select_users_cards_reviews_instances(
        session=session, select_one_instance=True, full_info=full_info, **filters
    )

    if not user_card_review:
        logger.warning("[DATABASE] User Card Reviews not found, params: %s", **filters)
        raise user_card_review_not_found_exception

    else:
        logger.info(
            "[DATABASE] User Card Review has been successfully selected, user_id: %s, user_card_id: %s",
            user_card_review.user_id,  # type: ignore
            user_card_review.user_card_id,  # type: ignore
        )
        return UserCardReviewSchema.model_validate(
            user_card_review, from_attributes=True
        )


async def update_user_card_review(  # type: ignore
    session: AsyncSessionDep,
    user_id: int,
    user_card_id: int,
    show_user: bool = False,
    **attrs
) -> UserCardReviewSchema:
    user_card_review = await select_users_cards_reviews_instances(
        session=session,
        select_one_instance=True,
        full_info=False,
        user_id=user_id,
        user_card_id=user_card_id,
    )
    if not user_card_review:
        logger.warning(
            "[DATABASE] User Card Review not found, user_id: %s, user_card_id: %s",
            user_id,
            user_card_id,
        )
        raise user_card_review_not_found_exception

    for key, value in attrs.items():
        if hasattr(user_card_review, key):
            setattr(user_card_review, key, value)

    try:
        await session.commit()
    except Exception:
        logger.error(
            "[DATABASE] Failed to update the user сard review, user_id: %s, user_card_id: %s",
            user_id,
            user_card_id,
        )
        raise update_user_card_review_exception

    if show_user:

        await session.refresh(user_card_review)

        return UserCardReviewSchema.model_validate(
            user_card_review, from_attributes=True
        )


async def select_users_cards_reviews(  # type: ignore
    session: AsyncSessionDep, full_info: bool = False, **filters
) -> List[UserCardReviewSchema]:
    users_cards_reviews = await select_users_cards_reviews_instances(
        session=session, full_info=full_info, select_one_instance=False, **filters
    )

    if not users_cards_reviews:
        logger.warning(
            "[DATABASE] Users Cards Reviews not found, params: %s", **filters
        )
        raise users_cards_reviews_not_found_exception

    logger.info(
        "[DATABASE] Users Cards Reviews have been successfully selected with params: %s",
        **filters
    )
    validated_users_cards_reviews = [
        UserCardReviewSchema.model_validate(user_card_review, from_attributes=True)
        for user_card_review in users_cards_reviews  # type: ignore
    ]

    return validated_users_cards_reviews


async def delete_user_card_review(session: AsyncSessionDep, **filters) -> bool:  # type: ignore
    user_card_review = await select_users_cards_reviews_instances(
        session=session, full_info=False, select_one_instance=True, **filters
    )

    if not user_card_review:
        logger.warning("[DATABASE] User Card Review not found, params: %s", **filters)
        raise user_card_review_not_found_exception

    else:
        await session.delete(user_card_review)
        logger.info(
            "[DATABASE] User Card Review has been successfully deleted with params: %s",
            **filters
        )

        return True
