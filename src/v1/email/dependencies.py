from fastapi import Form
from src.exceptions import invalid_email_code_exception


def validate_email_code(email_code: str = Form()) -> str:

    try:
        int(email_code)
    except ValueError:
        raise invalid_email_code_exception

    if len(email_code) != 6:
        raise invalid_email_code_exception

    return email_code
