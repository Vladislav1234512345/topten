from fastapi import APIRouter, Depends
from src.models import User
from src.v1.jwt.dependencies import get_current_admin_user_with_access_token


router = APIRouter()


@router.get('/protected')
async def protected(
        user: User = Depends(get_current_admin_user_with_access_token),
) -> User:
    return user