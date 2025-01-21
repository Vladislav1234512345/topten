from pydantic import BaseModel, field_validator, ValidationInfo

from src.exceptions import (
    invalid_sms_code_exception,
    different_passwords_exception,
    password_must_contain_a_digit_exception,
    password_must_contain_an_uppercase_letter_exception,
    password_min_length_exception,
)


class PhoneNumberSchema(BaseModel):
    phone_number: str


class VerificationCodeSchema(BaseModel):
    sms_code: str

    @field_validator("sms_code", mode="after")
    @classmethod
    def validate_sms_code(cls, value: str) -> str:
        try:
            int(value)
        except ValueError:
            raise invalid_sms_code_exception

        if len(value) != 6:
            raise invalid_sms_code_exception

        return value


class PasswordSchema(BaseModel):
    password: str

    @field_validator("password", mode="after")
    @classmethod
    def validate_password(cls, value) -> str:
        if len(value) < 8:
            raise password_min_length_exception
        if not any(char.isdigit() for char in value):
            raise password_must_contain_a_digit_exception
        if not any(char.isupper() for char in value):
            raise password_must_contain_an_uppercase_letter_exception
        return value


class PhoneNumberPasswordSchema(PhoneNumberSchema, PasswordSchema):
    pass


class TwoPasswordsSchema(PasswordSchema):
    password_reset: str

    @field_validator("password_reset", mode="after")
    @classmethod
    def check_passwords_match(cls, value: str, info: ValidationInfo) -> str:
        if value != info.data.get("password"):
            raise different_passwords_exception
        return value


class PhoneNumberVerificationCodeSchema(PhoneNumberSchema, VerificationCodeSchema):
    pass


class PhoneNumberPasswordVerificationCodeSchema(
    PhoneNumberPasswordSchema, VerificationCodeSchema
):
    pass


class PhoneNumberPasswordFirstNameVerificationCodeSchema(
    PhoneNumberPasswordVerificationCodeSchema
):
    first_name: str
