import phonenumbers
from fastapi import Form, HTTPException, status


def validate_phone_number(
        phone_number: str = Form()
) -> str:
    bad_request_exception = HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail = "Неверный номер телефона"
    )
    try:
        parsed_phone_number = phonenumbers.parse(number=phone_number)
    except:
        raise bad_request_exception

    if not phonenumbers.is_valid_number(parsed_phone_number):
        raise bad_request_exception

    return phone_number


def validate_sms_code(
        sms_code: str = Form()
) -> str:
    bad_request_exception = HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Неверный код подтверждения"
    )

    if len(sms_code) != 6:
        raise bad_request_exception

    return sms_code