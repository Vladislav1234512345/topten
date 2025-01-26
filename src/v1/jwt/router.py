from fastapi import APIRouter, Depends
from starlette.responses import JSONResponse

from ..users.schemas import UserSchema
from .dependencies import get_current_user_with_refresh_token
from .utils import set_tokens_in_response
from .responses import tokens_refresh_response
import logging
from src.container import configure_logging
from src.config import logging_settings

logger = logging.getLogger(__name__)
configure_logging(level=logging_settings.logging_level)

router = APIRouter()


@router.post("/refresh", response_model=UserSchema)
def refresh_tokens_view(
    user: UserSchema = Depends(get_current_user_with_refresh_token),
) -> JSONResponse:
    logger.info(
        f"User tokens have been successfully updated, phone number: %s",
        user.phone_number,
    )
    return set_tokens_in_response(response=tokens_refresh_response, user=user)
