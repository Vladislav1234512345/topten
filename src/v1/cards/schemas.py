import datetime
from typing import List

from pydantic import BaseModel, HttpUrl, Field, ConfigDict

from src.schemas import CardReviewSchema, UserCardServiceSchema
from src.v1.activities.schemas import ActivitySchema
from src.v1.users.schemas import UserSchema


class UserCardBaseSchema(BaseModel):
    activity_id: int


class UserCardCreateSchema(UserCardBaseSchema):
    card_image: HttpUrl
    description: str = Field(max_length=5000)
    experience: int = Field(default=0)


class UserCardSchema(UserCardCreateSchema):
    id: int
    user_id: int
    created_at: datetime.datetime
    updated_at: datetime.datetime

    user: "UserSchema"
    activity: "ActivitySchema"
    reviews: List["CardReviewSchema"]
    services: List["UserCardServiceSchema"]

    model_config = ConfigDict(from_attributes=True)


class UserCardUpdateSchema(UserCardBaseSchema):
    card_image: HttpUrl | None = None
    description: str | None = Field(max_length=5000)
    experience: int | None = Field(default=0)
