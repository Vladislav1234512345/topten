from pydantic import BaseModel, EmailStr, Field


class UserLoginSchema(BaseModel):
    email: EmailStr
    email_code: str = Field(min_length=6, max_length=6)
    password: str = Field(min_length=8)


class UserSignupSchema(BaseModel):
    email: EmailStr
    email_code: str = Field(min_length=6, max_length=6)
    password: str = Field(min_length=8)
    first_name: str = Field(min_length=1)