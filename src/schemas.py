from pydantic import BaseModel, ConfigDict, EmailStr, Field
import datetime


class UserBaseSchema(BaseModel):
    email: EmailStr
    first_name: str = Field(max_length=256)


class UserSchema(UserBaseSchema):
    id: int
    is_admin: bool
    is_stuff: bool
    is_active: bool
    created_at: datetime.datetime
    updated_at: datetime.datetime

    model_config = ConfigDict(from_attributes=True)


class UserPasswordSchema(UserSchema):
    password: bytes

    model_config = ConfigDict(from_attributes=True)

