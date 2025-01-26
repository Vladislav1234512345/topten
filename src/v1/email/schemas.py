from pydantic import BaseModel, Field, EmailStr, field_validator, ValidationInfo

from src.exceptions import (
    invalid_email_code_exception,
    different_passwords_exception,
    password_must_contain_a_digit_exception,
    password_must_contain_an_uppercase_letter_exception,
    password_min_length_exception,
)


class EmailSchema(BaseModel):
    email: EmailStr


class VerificationCodeSchema(BaseModel):
    email_code: str

    @field_validator("email_code", mode="after")
    @classmethod
    def validate_email_code(cls, value: str) -> str:
        try:
            int(value)
        except ValueError:
            raise invalid_email_code_exception

        if len(value) != 6:
            raise invalid_email_code_exception

        return value


class PasswordSchema(BaseModel):
    password: str

    @field_validator("password", mode="after")
    @classmethod
    def validate_password(cls, value: str) -> str:
        if len(value) < 8:
            raise password_min_length_exception
        if not any(char.isdigit() for char in value):
            raise password_must_contain_a_digit_exception
        if not any(char.isupper() for char in value):
            raise password_must_contain_an_uppercase_letter_exception
        return value


class EmailPasswordSchema(EmailSchema, PasswordSchema):
    pass


class TwoPasswordsSchema(PasswordSchema):
    password_reset: str

    @field_validator("password_reset", mode="after")
    @classmethod
    def check_passwords_match(cls, value: str, info: ValidationInfo) -> str:
        if value != info.data.get("password"):
            raise different_passwords_exception
        return value


class EmailVerificationCodeSchema(EmailSchema, VerificationCodeSchema):
    pass


class EmailPasswordVerificationCodeSchema(EmailPasswordSchema, VerificationCodeSchema):
    pass


class EmailPasswordFirstNameVerificationCodeSchema(EmailPasswordVerificationCodeSchema):
    first_name: str
