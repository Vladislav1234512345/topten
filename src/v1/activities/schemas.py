from typing import List

from pydantic import BaseModel, Field, ConfigDict

from src.v1.cards.schemas import UserCardSchema
from src.v1.users.schemas import UserSchema


class ActivityBaseSchema(BaseModel):
    name: str = Field(max_length=256)


class ActivitySchema(ActivityBaseSchema):
    id: int

    cards: List["UserCardSchema"]
    users: List["UserSchema"]

    model_config = ConfigDict(from_attributes=True)
