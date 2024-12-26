from sqlmodel import SQLModel, Field
from pydantic import EmailStr


class Base(SQLModel):
    id: int = Field(title="ID", primary_key=True)


class User(Base, table=True):
    __tablename__ = "users"

    email: EmailStr = Field(title="Email", unique=True, nullable=False)
    password: bytes = Field(title="Password", nullable=False, min_length=8)
    first_name: str = Field(title="First name", nullable=False, min_length=1)
    is_admin: bool = Field(title="Admin", default=False, nullable=True)
    is_stuff: bool = Field(title="Stuff", default=False, nullable=True)
    is_active: bool = Field(title="Active", default=True, nullable=True)
