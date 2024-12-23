from fastapi import Form, HTTPException, status

from models import User
from sqlmodel import Session, select


def validate_authorization(
        phone_number: str = Form(),

) -> User:
    unauthorized_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid phone number"
    )
    statement = select(User).filter_by(phone_number=phone_number)
    with Session() as session:
        user = session.exec(statement).first()

        if not user:
            raise unauthorized_exception

        return user