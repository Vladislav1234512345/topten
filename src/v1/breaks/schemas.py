from pydantic import BaseModel, ConfigDict

from src.v1.users.schemas import UserSchema
import datetime


class UserBreakBaseSchema(BaseModel):
    break_time: datetime.time


class UserBreakSchema(UserBreakBaseSchema):
    user_id: int
    id: int

    user: "UserSchema"

    model_config = ConfigDict(from_attributes=True)
