import datetime

from pydantic import BaseModel, Field, ConfigDict

from src.v1.cards.schemas import UserCardSchema
from src.v1.users.schemas import UserSchema


class UserCardReviewBaseSchema(BaseModel):
    user_card_id: int
    review_text: str = Field(max_length=2000)
    mark: int


class UserCardReviewSchema(UserCardReviewBaseSchema):
    user_id: int
    created_at: datetime.datetime
    updated_at: datetime.datetime

    user_sender: "UserSchema"
    card: "UserCardSchema"

    model_config = ConfigDict(from_attributes=True)


class UserCardReviewUpdateSchema(BaseModel):
    review_text: str | None = Field(max_length=2000)
    mark: int | None = None
