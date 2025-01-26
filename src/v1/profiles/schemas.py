import datetime

from pydantic import BaseModel, HttpUrl, ConfigDict

from src.models import GenderEnum
from src.v1.users.schemas import UserSchema


class ProfileBaseSchema(BaseModel):
    first_name: str


class ProfileSchema(ProfileBaseSchema):
    id: int
    user_id: int
    avatar: HttpUrl | None
    biography: str | None
    gender: GenderEnum | None
    birth_date: datetime.date | None
    created_at: datetime.datetime
    updated_at: datetime.datetime

    user: "UserSchema"

    model_config = ConfigDict(from_attributes=True)


class ProfileCreateAndUpdateSchema(BaseModel):
    first_name: str | None = None
    avatar: HttpUrl | None
    biography: str | None = None
    gender: GenderEnum | None = None
    birth_date: datetime.date | None = None

    model_config = ConfigDict(from_attributes=True)
