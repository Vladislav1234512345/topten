from fastapi.testclient import TestClient
from api.v1.jwt import router as jwt_router
from api.v1.email.utils import generate_email_code


client = TestClient(app=jwt_router)


def func_test_auth(phone_number: str, sms_code: str):
    response = client.post(url='/jwt/login', data={
    })
    assert response.status_code == 200
    assert response.json().get("access_token")
    assert response.json().get("refresh_token")


def test_auth():
    func_test_auth(phone_number='+77053872095', sms_code=generate_email_code())

