from pydantic import BaseModel, ConfigDict, EmailStr, Field
import datetime

from src.models import UserRole, GenderEnum


class UserBaseSchema(BaseModel):
    phone_number: str


class UserSchema(UserBaseSchema):
    id: int
    role: UserRole
    is_active: bool
    created_at: datetime.datetime
    updated_at: datetime.datetime

    model_config = ConfigDict(from_attributes=True)


class UserPasswordSchema(UserSchema):
    password: bytes

    model_config = ConfigDict(from_attributes=True)


class ProfileBaseSchema(BaseModel):
    first_name: str


class ProfileSchema(ProfileBaseSchema):
    id: int
    user_id: int
    avatar: str | None
    biography: str | None
    gender: GenderEnum | None
    birth_date: datetime.date | None
    created_at: datetime.datetime
    updated_at: datetime.datetime
