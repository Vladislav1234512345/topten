from fastapi.testclient import TestClient
from src.v1.email import router
import json


client = TestClient(router)


def test_reset_password(reset_password_body: dict[str, str], is_active: bool = False) -> None:
    if not is_active:
        return None
    response = client.post('/email/reset-password', content=json.dumps(reset_password_body))
    assert response.status_code == 200
    assert response.json() == {'message': 'Сообщение для сброса пароля успешно отправлено.'}


def test_verification_code(verification_code_body: dict[str, str], is_active: bool = False) -> None:
    if not is_active:
        return None
    response = client.post('/email/verification-code', content=json.dumps(verification_code_body))
    assert response.status_code == 200
    assert response.json() == {'message': 'Сообщение с кодом верификации успешно отправлено.'}



def test_send_emails():
    test_reset_password(
        reset_password_body={
            "email": "antonkutorov@gmail.com"
        },
        is_active=False
    )
    test_verification_code(
        verification_code_body={
            "email": "antonkutorov@gmail.com",
            "password": "qwerty1234",
        },
        is_active=True
    )