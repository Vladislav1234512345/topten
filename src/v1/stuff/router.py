from fastapi import APIRouter, Depends
from src.v1.users.schemas import UserSchema
from src.v1.jwt.dependencies import (
    get_current_stuff_role_and_higher_permission_with_access_token,
)
import logging
from src.container import configure_logging
from src.config import logging_settings

logger = logging.getLogger(__name__)
configure_logging(level=logging_settings.logging_level)


router = APIRouter()


@router.get("/protected", response_model=UserSchema)
async def protected_view(
    user: UserSchema = Depends(
        get_current_stuff_role_and_higher_permission_with_access_token
    ),
) -> UserSchema:
    logger.info(
        f"User successfully visited the protected page just for stuff, phone number: %s",
        user.phone_number,
    )
    return user
