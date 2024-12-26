from pydantic import BaseModel, Field, EmailStr


class EmailSchema(BaseModel):
    email: EmailStr


class VerificationCodeSchema(BaseModel):
    email_code: str = Field(min_length=6, max_length=6)


class EmailPasswordSchema(EmailSchema):
    password: str = Field(min_length=8)


class EmailVerificationCodeSchema(EmailSchema, VerificationCodeSchema):
    pass


class EmailPasswordVerificationCodeSchema(EmailPasswordSchema, VerificationCodeSchema):
    pass


class EmailPasswordFirstNameVerificationCodeSchema(EmailPasswordVerificationCodeSchema):
    first_name: str = Field(min_length=1)



