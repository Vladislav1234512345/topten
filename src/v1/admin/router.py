from fastapi import APIRouter, Depends
from src.schemas import UserSchema
from src.v1.jwt.dependencies import get_current_admin_user_with_access_token
import logging
from src.container import configure_logging
from src.config import logging_settings

logger = logging.getLogger(__name__)
configure_logging(level=logging_settings.logging_level)


router = APIRouter()


@router.get("/protected", response_model=UserSchema)
async def protected(
    user: UserSchema = Depends(get_current_admin_user_with_access_token),
) -> UserSchema:
    logger.info(
        f"User have successfully visited the protected page just for admins, email: %s",
        user.phone_number,
    )
    return user
