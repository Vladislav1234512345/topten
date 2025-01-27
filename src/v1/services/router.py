from typing import List

from fastapi import APIRouter
from fastapi.params import Depends
from starlette.responses import JSONResponse

from src.config import logging_settings
from src.database import AsyncSessionDep
from src.models import UserCardServiceModel
from src.v1.services.exceptions import (
    current_user_card_service_yet_exists_exception,
    create_user_card_service_forbidden_exception,
    delete_user_card_service_forbidden_exception,
)
from src.v1.services.responses import (
    user_card_service_is_deleted_response,
    user_card_service_is_created_response,
    user_card_service_is_updated_response,
)
from src.v1.services.schemas import (
    UserCardServiceBaseSchema,
    UserCardServiceSchema,
    UserCardServiceUpdateSchema,
)
from src.v1.services.utils import (
    create_user_card_service,
    delete_user_card_service,
    update_user_card_service,
    select_users_cards_services,
    select_user_card_service,
)
from src.v1.users.schemas import UserSchema

from src.v1.jwt.dependencies import (
    get_current_user_with_access_token,
)

from logging import getLogger
from src.container import configure_logging


logger = getLogger(__file__)
configure_logging(level=logging_settings.logging_level)

router = APIRouter()


@router.get("/{user_card_service_id}")
async def get_user_card_service_view(
    user_card_service_id: int,
    session: AsyncSessionDep,
    full_info: bool = False,
) -> UserCardServiceSchema:
    return await select_user_card_service(
        session=session, full_info=full_info, id=user_card_service_id
    )


@router.get("/")
async def get_users_cards_services_view(  # type: ignore
    session: AsyncSessionDep,
    full_info: bool = False,
    **filters,
) -> List[UserCardServiceSchema]:
    return await select_users_cards_services(
        session=session, full_info=full_info, **filters
    )


@router.patch("/{user_card_service_id}")
async def update_user_card_service_view(
    user_card_service_id: int,
    session: AsyncSessionDep,
    user_card_service_update_schema: UserCardServiceUpdateSchema,
    user: UserSchema = Depends(get_current_user_with_access_token),  # type: ignore
) -> JSONResponse:
    user_card_service_update_data = user_card_service_update_schema.model_dump(
        exclude_none=True
    )
    await update_user_card_service(
        session=session,
        user=user,
        user_card_service_id=user_card_service_id,
        **user_card_service_update_data,
    )
    logger.info(
        "User card service was successfully updated, user_id: %s, user_card_id: %s, user_card_service_id: %s",
        user.id,
        user_card_service_update_schema.user_card_id,
        user_card_service_id,
    )
    return user_card_service_is_updated_response


@router.delete("/{user_card_service_id}")
async def delete_user_card_service_view(
    user_card_service_id: int,
    session: AsyncSessionDep,
    user: UserSchema = Depends(get_current_user_with_access_token),  # type: ignore
) -> JSONResponse:
    await delete_user_card_service(session=session, user=user, id=user_card_service_id)
    logger.info(
        "User card service was successfully deleted, user_id: %s, user_card_service_id: %s",
        user.id,
        user_card_service_id,
    )
    return user_card_service_is_deleted_response


@router.post("/")
async def create_user_card_service_view(
    session: AsyncSessionDep,
    user_card_service_base_schema: UserCardServiceBaseSchema,
    user: UserSchema = Depends(get_current_user_with_access_token),  # type: ignore
) -> JSONResponse:
    user_cards_ids = [card.id for card in user.cards]
    if not user_card_service_base_schema.user_card_id in user_cards_ids:
        raise create_user_card_service_forbidden_exception
    user_card_service_data = user_card_service_base_schema.model_dump(exclude_none=True)
    user_card_service = await create_user_card_service(
        session=session,
        user_card_service=UserCardServiceModel(**user_card_service_data),
        exception=current_user_card_service_yet_exists_exception,
    )
    logger.info(
        "User card service was successfully created, user_id: %s, user_card_id: %s, user_card_service_id: %s, user_card_service name: %s",
        user.id,
        user_card_service.user_card_id,
        user_card_service.id,
        user_card_service.name,
    )
    return user_card_service_is_created_response
