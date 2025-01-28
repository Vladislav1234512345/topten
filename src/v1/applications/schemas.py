import datetime

from pydantic import BaseModel, Field, ConfigDict

from src.models import ApplicationStatusEnum
from src.v1.services.schemas import UserCardServiceSchema
from src.v1.users.schemas import UserSchema


class ApplicationBaseSchema(BaseModel):
    user_card_service_id: int
    application_date: datetime.date
    start_application_time: datetime.time
    finish_application_time: datetime.time
    application_status: ApplicationStatusEnum = Field(
        default=ApplicationStatusEnum.waiting
    )


class ApplicationSchema(ApplicationBaseSchema):
    id: int
    user_id: int
    created_at: datetime.datetime
    updated_at: datetime.datetime

    user_receiver: "UserSchema"
    service: "UserCardServiceSchema"

    model_config = ConfigDict(from_attributes=True)


class ApplicationUpdateSchema(BaseModel):
    application_date: datetime.date | None = None
    start_application_time: datetime.time | None = None
    finish_application_time: datetime.time | None = None
    application_status: ApplicationStatusEnum | None = Field(
        default=ApplicationStatusEnum.waiting
    )
