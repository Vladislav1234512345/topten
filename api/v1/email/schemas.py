from pydantic import BaseModel, EmailStr, Field


class UserSendEmailSchema(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)