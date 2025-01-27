from pydantic import BaseModel, ConfigDict

from src.v1.users.schemas import UserSchema
import datetime


class VacationDateBaseSchema(BaseModel):
    start_vacation_date: datetime.date
    finish_vacation_date: datetime.date


class UserVacationDateSchema(VacationDateBaseSchema):
    user_id: int
    id: int

    user: "UserSchema"

    model_config = ConfigDict(from_attributes=True)
