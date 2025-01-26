from pydantic import BaseModel, Field
from typing import List
import datetime

from src.models import ApplicationStatusEnum, WeekDayEnum
from src.v1.users.schemas import UserSchema
from src.v1.cards.schemas import UserCardSchema


class CardReviewSchema(BaseModel):
    id: int
    user_id: int
    user_card_id: int
    mark: int
    review_text: str = Field(max_length=2000)
    created_at: datetime.datetime
    updated_at: datetime.datetime

    user_sender: "UserSchema"
    card: "UserCardSchema"


class UserCardServiceSchema(BaseModel):
    id: int
    user_card_id: int
    name: str = Field(max_length=256)
    service_time: datetime.time
    cost: float

    card: "UserCardSchema"
    applications: List["ApplicationSchema"]


class ApplicationSchema(BaseModel):
    id: int
    user_id: int
    user_card_service_id: int
    application_date: datetime.date
    start_application_time: datetime.time
    finish_application_time: datetime.time
    application_status: ApplicationStatusEnum = Field(
        default=ApplicationStatusEnum.waiting
    )
    created_at: datetime.datetime
    updated_at: datetime.datetime

    user_receiver: "UserSchema"
    service: "UserCardServiceSchema"


class UserWeekDaySchema(BaseModel):
    id: int
    user_id: int
    week_day: WeekDayEnum
    is_work_day: bool
    start_work_time: datetime.time
    finish_work_time: datetime.time

    user: "UserSchema"


class UserBreakSchema(BaseModel):
    id: int
    user_id: int
    break_time: datetime.time

    user: "UserSchema"


class UserVacationTimeIntervalSchema(BaseModel):
    id: int
    user_id: int
    vacation_date: datetime.date
    start_vacation_time: datetime.time
    finish_vacation_time: datetime.time

    user: "UserSchema"


class UserVacationDateSchema(BaseModel):
    id: int
    user_id: int
    start_vacation_date: datetime.date
    finish_vacation_date: datetime.date

    user: "UserSchema"
