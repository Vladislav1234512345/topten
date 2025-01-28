from typing import List

from starlette.exceptions import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import selectinload, joinedload

from src.database import AsyncSessionDep
from src.v1.services.exceptions import (
    users_cards_services_not_found_exception,
    user_card_service_not_found_exception,
    update_user_card_service_exception,
    delete_user_card_service_forbidden_exception,
    update_user_card_service_forbidden_exception,
)
from src.schemas import UserCardServiceSchema, UserSchema
from src.models import UserCardServiceModel
import logging
from src.container import configure_logging
from src.config import logging_settings

logger = logging.getLogger(__name__)
configure_logging(level=logging_settings.logging_level)


async def create_user_card_service(
    user_card_service: UserCardServiceModel,
    session: AsyncSessionDep,
    exception: HTTPException,
) -> UserCardServiceSchema:
    session.add(user_card_service)
    try:
        await session.commit()
    except Exception:
        logger.warning(
            "[DATABASE] Current user card service has been existed yet, user_card_id: %s, user_card_service_id: %s, user_card_service name: %s",
            user_card_service.user_card_id,
            user_card_service.id,
            user_card_service.name,
        )
        raise exception
    await session.refresh(user_card_service)
    logger.info(
        "[DATABASE] User card service has been successfully created, user_card_id: %s, user_card_service_id: %s, user_card_service name: %s",
        user_card_service.user_card_id,
        user_card_service.id,
        user_card_service.name,
    )
    return UserCardServiceSchema.model_validate(user_card_service, from_attributes=True)


async def select_users_cards_services_instances(session: AsyncSessionDep, select_one_instance: bool = True, full_info: bool = True, **filters) -> UserCardServiceModel | List[UserCardServiceModel] | None:  # type: ignore
    statement = select(UserCardServiceModel).filter_by(**filters)
    if full_info:
        statement.options(
            joinedload(UserCardServiceModel.card),
            selectinload(UserCardServiceModel.applications),
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
                "[DATABASE] User card service not found, params: %s", **filters
            )
            raise user_card_service_not_found_exception
        else:
            logger.warning(
                "[DATABASE] Users cards services not found, params: %s", **filters
            )
            raise users_cards_services_not_found_exception


async def select_user_card_service(  # type: ignore
    session: AsyncSessionDep, full_info: bool = False, **filters
) -> UserCardServiceSchema:
    user_card_service = await select_users_cards_services_instances(
        session=session, select_one_instance=True, full_info=full_info, **filters
    )

    if not user_card_service:
        logger.warning("[DATABASE] User card service not found, params: %s", **filters)
        raise user_card_service_not_found_exception

    logger.info(
        "[DATABASE] User break has been successfully selected, user_card_id: %s, user_card_service_id: %s, user_card_service name: %s",
        user_card_service.user_card_id,  # type: ignore
        user_card_service.id,  # type: ignore
        user_card_service.name,  # type: ignore
    )
    return UserCardServiceSchema.model_validate(user_card_service, from_attributes=True)


async def update_user_card_service(  # type: ignore
    session: AsyncSessionDep,
    user: UserSchema,
    user_card_service_id: int,
    show_user: bool = False,
    **attrs
) -> UserCardServiceSchema:
    user_card_service = await select_users_cards_services_instances(
        session=session,
        select_one_instance=True,
        full_info=False,
        id=user_card_service_id,
    )
    user_cards_ids = [card.id for card in user.cards]
    if not user_card_service.user_card_id in user_cards_ids:  # type: ignore
        raise update_user_card_service_forbidden_exception

    if not user_card_service:
        logger.warning(
            "[DATABASE] User card service not found, user_card_service_id: %s",
            user_card_service_id,
        )
        raise user_card_service_not_found_exception

    for key, value in attrs.items():
        if hasattr(user_card_service, key):
            setattr(user_card_service, key, value)

    try:
        await session.commit()
    except Exception:
        logger.error(
            "[DATABASE] Failed to update the user card service, user_card_service_id: %s",
            user_card_service_id,
        )
        raise update_user_card_service_exception

    if show_user:

        await session.refresh(user_card_service)

        logger.info(
            "[DATABASE] User card service has been successfully updated, user_card_service_id: %s and attrs: %s",
            user_card_service_id,
            **attrs
        )

        return UserCardServiceSchema.model_validate(
            user_card_service, from_attributes=True
        )


async def select_users_cards_services(  # type: ignore
    session: AsyncSessionDep, full_info: bool = False, **filters
) -> List[UserCardServiceSchema]:
    users_cards_services = await select_users_cards_services_instances(
        session=session, full_info=full_info, select_one_instance=False, **filters
    )

    if not users_cards_services:
        logger.warning(
            "[DATABASE] Users cards services not found, params: %s", **filters
        )
        raise users_cards_services_not_found_exception

    logger.info(
        "[DATABASE] Users cards services have been successfully selected with params: %s",
        **filters
    )
    validated_users_cards_services = [UserCardServiceSchema.model_validate(user_card_service, from_attributes=True) for user_card_service in users_cards_services]  # type: ignore

    return validated_users_cards_services


async def delete_user_card_service(session: AsyncSessionDep, user: UserSchema, **filters) -> bool:  # type: ignore
    user_card_service = await select_users_cards_services_instances(
        session=session, full_info=False, select_one_instance=True, **filters
    )
    user_cards_ids = [card.id for card in user.cards]
    if not user_card_service.user_card_id in user_cards_ids:  # type: ignore
        raise delete_user_card_service_forbidden_exception
    if not user_card_service:
        logger.warning("[DATABASE] User card service not found, params: %s", **filters)
        raise user_card_service_not_found_exception

    await session.delete(user_card_service)

    logger.info(
        "[DATABASE] User card service has been successfully deleted with params: %s",
        **filters
    )

    return True
