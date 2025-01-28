from pydantic import BaseModel, ConfigDict, Field
from typing import List

from src.v1.applications.schemas import ApplicationSchema
from src.v1.cards.schemas import UserCardSchema
import datetime


class UserCardServiceBaseSchema(BaseModel):
    user_card_id: int
    name: str = Field(max_length=256)
    service_time: datetime.time
    cost: float


class UserCardServiceUpdateSchema(BaseModel):
    user_card_id: int | None = None
    name: str | None = None
    service_time: datetime.time | None = None
    cost: float | None = None


class UserCardServiceSchema(UserCardServiceBaseSchema):
    id: int

    card: "UserCardSchema"
    applications: List["ApplicationSchema"]

    model_config = ConfigDict(from_attributes=True)
