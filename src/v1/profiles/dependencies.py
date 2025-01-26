from typing import Any

from fastapi import Depends

from src.database import AsyncSessionDep
from src.v1.users.schemas import UserSchema
from src.v1.profiles.schemas import ProfileSchema
from src.v1.profiles.utils import select_profile
from src.v1.jwt.dependencies import get_current_user_with_access_token


class ProfileGetterFromUserAccessToken:
    async def __call__(
        self,
        session: AsyncSessionDep,
        user: UserSchema = Depends(get_current_user_with_access_token),
    ) -> ProfileSchema:
        return await select_profile(session=session, user_id=user.id)


get_current_profile_with_user = ProfileGetterFromUserAccessToken()
