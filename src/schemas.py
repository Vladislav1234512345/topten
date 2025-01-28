import datetime
from typing import List, Optional

from pydantic import ConfigDict, HttpUrl, BaseModel, Field

from src.models import GenderEnum, UserRole, ApplicationStatusEnum, WeekDayEnum


class UserCardServiceBaseSchema(BaseModel):
    user_card_id: int
    name: str = Field(max_length=256)
    service_time: datetime.time
    cost: float


class UserCardServiceSchema(UserCardServiceBaseSchema):
    id: int

    card: "UserCardSchema"
    applications: List["ApplicationSchema"]

    model_config = ConfigDict(from_attributes=True)


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


class ProfileBaseSchema(BaseModel):
    first_name: str


class ProfileSchema(ProfileBaseSchema):
    id: int
    user_id: int
    avatar: HttpUrl | None
    biography: str | None
    gender: GenderEnum | None
    birth_date: datetime.date | None
    created_at: datetime.datetime
    updated_at: datetime.datetime

    user: "UserSchema"

    model_config = ConfigDict(from_attributes=True)


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
    reviews: List["UserCardReviewSchema"]
    services: List["UserCardServiceSchema"]

    model_config = ConfigDict(from_attributes=True)


class UserBreakBaseSchema(BaseModel):
    break_time: datetime.time


class UserBreakSchema(UserBreakBaseSchema):
    user_id: int
    id: int

    user: "UserSchema"

    model_config = ConfigDict(from_attributes=True)


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


class ActivityBaseSchema(BaseModel):
    name: str = Field(max_length=256)


class ActivitySchema(ActivityBaseSchema):
    id: int

    cards: List["UserCardSchema"]
    users: List["UserSchema"]

    model_config = ConfigDict(from_attributes=True)


class UserBaseSchema(BaseModel):
    phone_number: str


class UserSchema(UserBaseSchema):
    id: int
    role: UserRole
    is_active: bool
    created_at: datetime.datetime
    updated_at: datetime.datetime


class UserFullInfoSchema(UserSchema):

    profile: Optional["ProfileSchema"]
    cards: List["UserCardSchema"] | None
    break_time: Optional["UserBreakSchema"]
    vacations_times: List["UserVacationTimeSchema"] | None
    vacations_dates: List["UserVacationDateSchema"] | None
    week_days: List["UserWeekDaySchema"] | None
    applications: List["ApplicationSchema"] | None
    sent_reviews: List["UserCardReviewSchema"] | None
    activities: List["ActivitySchema"] | None

    model_config = ConfigDict(from_attributes=True)


class UserPasswordFullInfoSchema(UserFullInfoSchema):
    password: bytes | None

    model_config = ConfigDict(from_attributes=True)


class ApplicationUpdateSchema(BaseModel):
    application_date: datetime.date | None = None
    start_application_time: datetime.time | None = None
    finish_application_time: datetime.time | None = None
    application_status: ApplicationStatusEnum | None = Field(
        default=ApplicationStatusEnum.waiting
    )


class UserCardBaseSchema(BaseModel):
    activity_id: int


class UserCardUpdateSchema(UserCardBaseSchema):
    card_image: HttpUrl | None = None
    description: str | None = Field(max_length=5000)
    experience: int | None = Field(default=0)


class ProfileCreateAndUpdateSchema(BaseModel):
    first_name: str | None = None
    avatar: HttpUrl | None
    biography: str | None = None
    gender: GenderEnum | None = None
    birth_date: datetime.date | None = None

    model_config = ConfigDict(from_attributes=True)


class UserCardReviewUpdateSchema(BaseModel):
    review_text: str | None = Field(max_length=2000)
    mark: int | None = None


class UserCardServiceUpdateSchema(BaseModel):
    user_card_id: int | None = None
    name: str | None = None
    service_time: datetime.time | None = None
    cost: float | None = None


class UserPasswordSchema(UserSchema):
    password: bytes | None

    model_config = ConfigDict(from_attributes=True)


class UserCreateAndUpdateSchema(BaseModel):
    phone_number: str | None = None
    is_active: bool | None = None
    role: UserRole | None = None
    password: bytes | None = None


class VacationDateBaseSchema(BaseModel):
    start_vacation_date: datetime.date
    finish_vacation_date: datetime.date


class UserVacationDateSchema(VacationDateBaseSchema):
    user_id: int
    id: int

    user: "UserSchema"

    model_config = ConfigDict(from_attributes=True)


class VacationDateSchema(BaseModel):
    vacation_date: datetime.date = Field(default=datetime.date.today())


class VacationTimeBaseSchema(BaseModel):
    start_vacation_time: datetime.time
    finish_vacation_time: datetime.time


class VacationTimeAndDateBaseSchema(VacationTimeBaseSchema, VacationDateSchema):
    pass


class UserVacationTimeSchema(VacationTimeBaseSchema, VacationDateSchema):
    user_id: int
    id: int

    user: "UserSchema"

    model_config = ConfigDict(from_attributes=True)


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
