from sqlmodel import SQLModel, Field


class Base(SQLModel):
    id: int = Field(title="ID", primary_key=True)


class User(Base, table=True):
    __tablename__ = "users"

    phone_number: str = Field(title="Phone number", unique=True)
    first_name: str = Field(title="First name")
    is_admin: bool = Field(title="Admin", default=False)
