from typing import List

from starlette.exceptions import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from src.database import AsyncSessionDep
from src.v1.applications.exceptions import (
    update_application_exception,
    application_not_found_exception,
    applications_not_found_exception,
    update_application_forbidden_exception,
)

from src.models import ApplicationModel, UserCardServiceModel, UserCardModel
from src.schemas import ApplicationSchema
import logging
from src.container import configure_logging
from src.config import logging_settings


logger = logging.getLogger(__name__)
configure_logging(level=logging_settings.logging_level)


async def create_application(
    application: ApplicationModel, session: AsyncSessionDep, exception: HTTPException
) -> ApplicationSchema:
    session.add(application)
    try:
        await session.commit()
    except Exception:
        logger.warning(
            "[DATABASE] Current application has been existed yet, user_id: %s, user_card_service_id: %s",
            application.user_id,
            application.user_card_service_id,
        )
        raise exception
    await session.refresh(application)
    logger.info(
        "[DATABASE] User Card has been successfully created, application_id: %s, user_id: %s, user_card_service_id: %s",
        application.id,
        application.user_id,
        application.user_card_service_id,
    )
    return ApplicationSchema.model_validate(application, from_attributes=True)


async def select_applications_instances(session: AsyncSessionDep, select_one_instance: bool = True, full_info: bool = True, **filters) -> ApplicationModel | List[ApplicationModel] | None:  # type: ignore
    statement = select(ApplicationModel).filter_by(**filters)
    if full_info:
        statement.options(
            joinedload(ApplicationModel.service)
            .joinedload(UserCardServiceModel.card)
            .joinedload(UserCardModel.user),
        )
    try:
        result = await session.execute(statement)
        if select_one_instance:
            return result.scalar()
        else:
            return list(result.scalars().all())
    except:
        if select_one_instance:
            logger.warning("[DATABASE] Application not found, params: %s", **filters)
            raise application_not_found_exception
        else:
            logger.warning("[DATABASE] Applications not found, params: %s", **filters)
            raise application_not_found_exception


async def select_application(  # type: ignore
    session: AsyncSessionDep, full_info: bool = False, **filters
) -> ApplicationSchema:
    application = await select_applications_instances(
        session=session, select_one_instance=True, full_info=full_info, **filters
    )

    if not application:
        logger.warning("[DATABASE] Application not found, params: %s", **filters)
        raise application_not_found_exception

    else:
        logger.info(
            "[DATABASE] Application has been successfully selected, application_id: %s, user_id: %s, user_card_service_id: %s",
            application.id,  # type: ignore
            application.user_id,  # type: ignore
            application.user_card_service_id,  # type: ignore
        )
        return ApplicationSchema.model_validate(application, from_attributes=True)


async def update_application(  # type: ignore
    session: AsyncSessionDep,
    current_user_id: int,
    application_id: int,
    show_user: bool = False,
    **attrs
) -> ApplicationSchema:
    application = await select_applications_instances(
        session=session,
        select_one_instance=True,
        full_info=True,
        id=application_id,
    )

    if not application:
        logger.warning(
            "[DATABASE] Application not found, application: %s",
            application_id,
        )
        raise application_not_found_exception

    user_producer = application.service.card.user  # type: ignore

    if user_producer != current_user_id:
        raise update_application_forbidden_exception

    for key, value in attrs.items():
        if hasattr(application, key):
            setattr(application, key, value)

    try:
        await session.commit()
    except Exception:
        logger.error(
            "[DATABASE] Failed to update the application, application_id: %s",
            application_id,
        )
        raise update_application_exception

    if show_user:

        await session.refresh(application)

        return ApplicationSchema.model_validate(application, from_attributes=True)


async def select_applications(  # type: ignore
    session: AsyncSessionDep, full_info: bool = False, **filters
) -> List[ApplicationSchema]:
    applications = await select_applications_instances(
        session=session, full_info=full_info, select_one_instance=False, **filters
    )

    if not applications:
        logger.warning("[DATABASE] Applications not found, params: %s", **filters)
        raise applications_not_found_exception

    logger.info(
        "[DATABASE] Applications have been successfully selected with params: %s",
        **filters
    )
    validated_applications = [
        ApplicationSchema.model_validate(application, from_attributes=True)
        for application in applications  # type: ignore
    ]

    return validated_applications


async def delete_application(session: AsyncSessionDep, **filters) -> bool:  # type: ignore
    application = await select_applications_instances(
        session=session, full_info=False, select_one_instance=True, **filters
    )

    if not application:
        logger.warning("[DATABASE] Application not found, params: %s", **filters)
        raise application_not_found_exception

    await session.delete(application)
    logger.info(
        "[DATABASE] Application has been successfully deleted with params: %s",
        **filters
    )

    return True
