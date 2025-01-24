from sqlalchemy import ForeignKey, String, Time, Date
from sqlalchemy_utils import URLType
from sqlalchemy.orm import mapped_column, Mapped, relationship
from src.database import intpk, str_256, created_at, updated_at, BaseModel
from typing import List, Optional
import enum
import datetime


class GenderEnum(str, enum.Enum):
    male = "male"
    female = "female"


class UserRole(int, enum.Enum):
    user = 10
    stuff = 50
    admin = 100
    superuser = 1000


class WeekDayEnum(str, enum.Enum):
    monday = "monday"
    tuesday = "tuesday"
    wednesday = "wednesday"
    thursday = "thursday"
    friday = "friday"
    saturday = "saturday"
    sunday = "sunday"


class ApplicationStatusEnum(str, enum.Enum):
    accepted = "accepted"
    rejected = "rejected"
    waiting = "waiting"


class UserModel(BaseModel):
    __tablename__ = "users"

    id: Mapped[intpk]
    phone_number: Mapped[str] = mapped_column(
        String(length=50), nullable=False, unique=True
    )
    password: Mapped[bytes] = mapped_column(nullable=False)
    role: Mapped[int] = mapped_column(default=UserRole.user, nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)
    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]

    profile: Mapped["ProfileModel"] = relationship(back_populates="user")
    break_time: Mapped["UserBreakModel"] = relationship(back_populates="user")
    vacations_time_intervals: Mapped[List["UserVacationTimeIntervalModel"]] = (
        relationship(back_populates="user")
    )
    vacations_dates: Mapped[List["UserVacationDateModel"]] = relationship(
        back_populates="user"
    )
    cards: Mapped[List["UserCardModel"]] = relationship(back_populates="user")
    week_days: Mapped[List["UserWeekDayModel"]] = relationship(back_populates="user")
    applications: Mapped[List["ApplicationModel"]] = relationship(back_populates="user")

    activities: Mapped[List["ActivityModel"]] = relationship(
        back_populates="users", secondary="users_activities"
    )


class ProfileModel(BaseModel):
    __tablename__ = "profiles"

    id: Mapped[intpk]
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    first_name: Mapped[str_256] = mapped_column(nullable=False)
    avatar: Mapped[Optional[str]] = mapped_column(URLType, nullable=True)
    biography: Mapped[Optional[str]] = mapped_column(String(length=500), nullable=True)
    gender: Mapped[Optional["GenderEnum"]] = mapped_column(nullable=True)
    birth_date: Mapped[Optional[datetime.date]] = mapped_column(Date, nullable=True)
    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]

    user: Mapped["UserModel"] = relationship(back_populates="profile")


class UserBreakModel(BaseModel):
    __tablename__ = "users_breaks"

    id: Mapped[intpk]
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    break_time: Mapped[datetime.time] = mapped_column(
        Time, nullable=False, default=datetime.time()
    )

    user: Mapped["UserModel"] = relationship(back_populates="break_time")


class UserVacationTimeIntervalModel(BaseModel):
    __tablename__ = "users_vacations_time_intervals"

    id: Mapped[intpk]
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    vacation_date: Mapped[datetime.date] = mapped_column(
        Date,
        nullable=False,
    )
    start_vacation_time: Mapped[datetime.time] = mapped_column(Time, nullable=False)
    finish_vacation_time: Mapped[datetime.time] = mapped_column(Time, nullable=False)

    user: Mapped["UserModel"] = relationship(back_populates="vacations_time_intervals")


class UserVacationDateModel(BaseModel):
    __tablename__ = "users_vacations_dates"

    id: Mapped[intpk]
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    start_vacation_date: Mapped[datetime.date] = mapped_column(
        Date,
        nullable=False,
    )
    finish_vacation_date: Mapped[datetime.date] = mapped_column(
        Date,
        nullable=False,
    )

    user: Mapped["UserModel"] = relationship(back_populates="vacations_dates")


class UserCardModel(BaseModel):
    __tablename__ = "users_cards"

    id: Mapped[intpk]
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    activity_id: Mapped[int] = mapped_column(
        ForeignKey("activities.id", ondelete="CASCADE"),
        nullable=False,
    )
    card_image: Mapped[str] = mapped_column(URLType, nullable=False)
    description: Mapped[str] = mapped_column(String(length=5000), nullable=False)
    experience: Mapped[int] = mapped_column(nullable=False, default=0)
    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]

    user: Mapped["UserModel"] = relationship(back_populates="cards")
    activity: Mapped["ActivityModel"] = relationship(back_populates="cards")
    reviews: Mapped[List["CardReviewModel"]] = relationship(back_populates="card")
    services: Mapped[List["UserCardServiceModel"]] = relationship(back_populates="card")


class ActivityModel(BaseModel):
    __tablename__ = "activities"

    id: Mapped[intpk]
    name: Mapped[str_256] = mapped_column(nullable=False, unique=True)

    cards: Mapped[List["UserCardModel"]] = relationship(back_populates="activity")

    users: Mapped[List["UserModel"]] = relationship(
        back_populates="activities", secondary="users_activities"
    )


class UserActivityModel(BaseModel):
    __tablename__ = "users_activities"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), primary_key=True, nullable=False
    )
    activity_id: Mapped[int] = mapped_column(
        ForeignKey("activities.id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
    )


class CardReviewModel(BaseModel):
    __tablename__ = "cards_reviews"

    id: Mapped[intpk]
    user_card_id: Mapped[int] = mapped_column(
        ForeignKey("users_cards.id", ondelete="CASCADE"), nullable=False
    )
    mark: Mapped[int] = mapped_column(
        nullable=False,
    )
    review_text: Mapped[str] = mapped_column(String(length=2000), nullable=False)
    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]

    card: Mapped["UserCardModel"] = relationship(back_populates="reviews")


class UserCardServiceModel(BaseModel):
    __tablename__ = "users_cards_services"

    id: Mapped[intpk]
    user_card_id: Mapped[int] = mapped_column(
        ForeignKey("users_cards.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str_256] = mapped_column(nullable=False)
    service_time: Mapped[datetime.time] = mapped_column(nullable=False)
    cost: Mapped[float] = mapped_column(nullable=False)

    card: Mapped["UserCardModel"] = relationship(back_populates="services")
    applications: Mapped[List["ApplicationModel"]] = relationship(
        back_populates="service"
    )


class ApplicationModel(BaseModel):
    __tablename__ = "applications"

    id: Mapped[intpk]
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    user_card_service_id: Mapped[int] = mapped_column(
        ForeignKey("users_cards_services.id", ondelete="CASCADE"), nullable=False
    )
    application_date: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    start_application_time: Mapped[datetime.time] = mapped_column(Time, nullable=False)
    finish_application_time: Mapped[datetime.time] = mapped_column(Time, nullable=False)
    application_status: Mapped["ApplicationStatusEnum"] = mapped_column(
        nullable=False, default=ApplicationStatusEnum.waiting
    )
    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]

    user: Mapped["UserModel"] = relationship(back_populates="applications")
    service: Mapped["UserCardServiceModel"] = relationship(
        back_populates="applications"
    )


class UserWeekDayModel(BaseModel):
    __tablename__ = "users_week_days"

    id: Mapped[intpk]
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    week_day: Mapped[WeekDayEnum] = mapped_column(nullable=False)
    is_work_day: Mapped[bool] = mapped_column(nullable=False)
    start_work_time: Mapped[datetime.time] = mapped_column(Time, nullable=False)
    finish_work_time: Mapped[datetime.time] = mapped_column(Time, nullable=False)

    user: Mapped["UserModel"] = relationship(back_populates="week_days")
