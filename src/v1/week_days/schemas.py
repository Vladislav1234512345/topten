from pydantic import BaseModel, ConfigDict, Field

from src.models import WeekDayEnum
from src.v1.users.schemas import UserSchema
import datetime


class WeekDayBaseSchema(BaseModel):
    week_day: WeekDayEnum


class WorkTimeBaseSchema(BaseModel):
    start_work_time: datetime.time = Field(default=datetime.time(minute=0))
    finish_work_time: datetime.time = Field(datetime.time(minute=0))


class WeekDaySchema(WeekDayBaseSchema, WorkTimeBaseSchema):
    pass


class UserWeekDaySchema(WeekDaySchema):
    user_id: int
    id: int

    user: "UserSchema"

    model_config = ConfigDict(from_attributes=True)
