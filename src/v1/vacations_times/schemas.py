from pydantic import BaseModel, ConfigDict, Field

from src.v1.users.schemas import UserSchema
import datetime


class VacationDateBaseSchema(BaseModel):
    vacation_date: datetime.date = Field(default=datetime.date.today())


class VacationTimeBaseSchema(BaseModel):
    start_vacation_time: datetime.time
    finish_vacation_time: datetime.time


class VacationTimeAndDateBaseSchema(VacationTimeBaseSchema, VacationDateBaseSchema):
    pass


class UserVacationTimeSchema(VacationTimeBaseSchema, VacationDateBaseSchema):
    user_id: int
    id: int

    user: "UserSchema"

    model_config = ConfigDict(from_attributes=True)
