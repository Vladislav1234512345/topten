from typing import List

from starlette.exceptions import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import joinedload, selectinload

from src.database import AsyncSessionDep
from src.v1.cards.exceptions import (
    update_user_card_exception,
    user_card_not_found_exception,
    users_cards_not_found_exception,
)

from src.v1.users.exceptions import user_not_found_exception, users_not_found_exception
from src.models import UserCardModel, UserModel
from src.v1.cards.schemas import UserCardSchema
import logging
from src.container import configure_logging
from src.config import logging_settings


logger = logging.getLogger(__name__)
configure_logging(level=logging_settings.logging_level)


async def create_user_card(
    user_card: UserCardModel, session: AsyncSessionDep, exception: HTTPException
) -> UserCardSchema:
    session.add(user_card)
    try:
        await session.commit()
    except Exception:
        logger.warning(
            "[DATABASE] Current user cards has been existed yet, user_id: %s, activity_id: %s",
            user_card.user_id,
            user_card.activity_id,
        )
        raise exception
    await session.refresh(user_card)
    logger.info(
        "[DATABASE] User Card has been successfully created, user_card_id: %s, user_id: %s, activity_id: %s",
        user_card.id,
        user_card.user_id,
        user_card.activity_id,
    )
    return UserCardSchema.model_validate(user_card, from_attributes=True)


async def select_users_cards_instances(session: AsyncSessionDep, select_one_instance: bool = True, full_info: bool = True, **filters) -> UserCardModel | List[UserCardModel] | None:  # type: ignore
    statement = select(UserCardModel).filter_by(**filters)
    if full_info:
        statement.options(
            joinedload(UserCardModel.user),
            joinedload(UserCardModel.activity),
            joinedload(UserModel.profile),
            selectinload(UserCardModel.card_reviews),
            selectinload(UserCardModel.services),
        )
    try:
        result = await session.execute(statement)
        if select_one_instance:
            return result.scalar()
        else:
            return list(result.scalars().all())
    except:
        if select_one_instance:
            logger.warning("[DATABASE] User Card not found, params: %s", filters)
            raise user_not_found_exception
        else:
            logger.warning("[DATABASE] Users Cards not found, params: %s", filters)
            raise users_not_found_exception


async def select_user_card(  # type: ignore
    session: AsyncSessionDep, full_info: bool = False, **filters
) -> UserCardSchema:
    user_card = await select_users_cards_instances(
        session=session, select_one_instance=True, full_info=full_info, **filters
    )

    if not user_card:
        logger.warning("[DATABASE] User Card not found, params: %s", **filters)
        raise user_card_not_found_exception

    else:
        logger.info(
            "[DATABASE] User Card has been successfully selected, user_card_id: %s, user_id: %s, activity_id: %s",
            user_card.id,  # type: ignore
            user_card.user_id,  # type: ignore
            user_card.activity_id,  # type: ignore
        )
        return UserCardSchema.model_validate(user_card, from_attributes=True)


async def update_user_card_with_id(  # type: ignore
    session: AsyncSessionDep, user_card_id: int, show_user: bool = False, **attrs
) -> UserCardSchema:
    user_card = await select_users_cards_instances(
        session=session, select_one_instance=True, full_info=False, id=user_card_id
    )
    if not user_card:
        logger.warning("[DATABASE] User Card not found, user_card_id: %s", user_card_id)
        raise user_card_not_found_exception

    for key, value in attrs.items():
        if hasattr(user_card, key):
            setattr(user_card, key, value)

    try:
        await session.commit()
    except Exception:
        logger.error(
            "[DATABASE] Failed to update the user сard, user_card_id: %s, user_id: %s, activity_id: %s",
            user_card_id,
            user_card.user_id,  # type: ignore
            user_card.activity_id,  # type: ignore
        )
        raise update_user_card_exception

    if show_user:

        await session.refresh(user_card)

        return UserCardSchema.model_validate(user_card, from_attributes=True)


async def update_user_card_with_user_and_activity_ids(  # type: ignore
    session: AsyncSessionDep,
    user_id: int,
    activity_id: int,
    show_user: bool = False,
    **attrs
) -> UserCardSchema:
    user_card = await select_users_cards_instances(
        session=session,
        select_one_instance=True,
        full_info=False,
        user_id=user_id,
        activity_id=activity_id,
    )
    if not user_card:
        logger.warning(
            "[DATABASE] User Card not found, user_id: %s, activity_id: %s",
            user_id,
            activity_id,
        )
        raise user_card_not_found_exception

    for key, value in attrs.items():
        if hasattr(user_card, key):
            setattr(user_card, key, value)

    try:
        await session.commit()
    except Exception:
        logger.error(
            "[DATABASE] Failed to update the user сard, user_card_id: %s, user_id: %s, activity_id: %s",
            user_card.id,  # type: ignore
            user_id,
            activity_id,
        )
        raise update_user_card_exception

    if show_user:

        await session.refresh(user_card)

        return UserCardSchema.model_validate(user_card, from_attributes=True)


async def select_users_cards(  # type: ignore
    session: AsyncSessionDep, full_info: bool = False, **filters
) -> List[UserCardSchema]:
    users_cards = await select_users_cards_instances(
        session=session, full_info=full_info, select_one_instance=False, **filters
    )

    if not users_cards:
        logger.warning("[DATABASE] Users Cards not found, params: %s", **filters)
        raise users_cards_not_found_exception

    logger.info(
        "[DATABASE] Users Cards have been successfully selected with params: %s",
        **filters
    )
    validated_users_cards = [
        UserCardSchema.model_validate(user_card, from_attributes=True)
        for user_card in users_cards  # type: ignore
    ]

    return validated_users_cards


async def delete_user_card(session: AsyncSessionDep, **filters) -> bool:  # type: ignore
    user_card = await select_users_cards_instances(
        session=session, full_info=False, select_one_instance=True, **filters
    )

    if not user_card:
        logger.warning("[DATABASE] User Card not found, params: %s", **filters)
        raise user_not_found_exception

    await session.delete(user_card)
    logger.info(
        "[DATABASE] User Card has been successfully deleted with params: %s", **filters
    )

    return True
