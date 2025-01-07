from fastapi import APIRouter, Depends
from src.schemas import UserSchema
from src.v1.jwt.dependencies import get_current_admin_user_with_access_token


router = APIRouter()


@router.get('/protected', response_model=UserSchema)
async def protected(
        user: UserSchema = Depends(get_current_admin_user_with_access_token),
) -> UserSchema:
    return user