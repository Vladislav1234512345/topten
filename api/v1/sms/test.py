from fastapi.testclient import TestClient
from api.v1.sms import router as sms_router

client = TestClient(app=sms_router)

def func_test_send_sms_send(phone_number: str):
    response = client.post('/sms/send', data={'phone_number': phone_number})
    assert response.status_code == 200
    assert response.json() == {"message": "Код отправлен"}


def test_send_sms_send():
    func_test_send_sms_send('+77053872095')
    func_test_send_sms_send('+79991709804')
    func_test_send_sms_send('+77053872093')
