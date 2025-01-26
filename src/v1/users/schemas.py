import datetime
from typing import List

from pydantic import BaseModel, ConfigDict

from src.models import UserRole
from src.schemas import (
    UserBreakSchema,
    UserVacationTimeIntervalSchema,
    UserVacationDateSchema,
    UserWeekDaySchema,
    ApplicationSchema,
    CardReviewSchema,
)
from src.v1.activities.schemas import ActivitySchema
from src.v1.cards.schemas import UserCardSchema
from src.v1.profiles.schemas import ProfileSchema


class UserBaseSchema(BaseModel):
    phone_number: str


class UserSchema(UserBaseSchema):
    id: int
    role: UserRole
    is_active: bool
    created_at: datetime.datetime
    updated_at: datetime.datetime

    profile: "ProfileSchema"
    cards: List["UserCardSchema"]
    break_time: "UserBreakSchema"
    vacations_time_intervals: List["UserVacationTimeIntervalSchema"]
    vacations_dates: List["UserVacationDateSchema"]
    week_days: List["UserWeekDaySchema"]
    applications: List["ApplicationSchema"]
    sent_reviews: List["CardReviewSchema"]

    activities: List["ActivitySchema"]

    model_config = ConfigDict(from_attributes=True)


class UserPasswordSchema(UserSchema):
    password: bytes

    model_config = ConfigDict(from_attributes=True)


class UserCreateAndUpdateSchema(BaseModel):
    phone_number: str | None = None
    is_active: bool | None = None
    role: UserRole | None = None
    password: bytes | None = None
