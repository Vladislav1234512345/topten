from fastapi.testclient import TestClient
from api.v1.email import router as email_router

client = TestClient(app=email_router)

def func_test_send_email(email: str):
    response = client.post('/email/send', json={"email": email})
    assert response.status_code == 200
    assert response.json() == {"message": "Код отправлен"}


def test_send_email():
    func_test_send_email('tolerantniy2104@gmail.com')
    func_test_send_email('/tolerantniy2104@gmail.com')
    func_test_send_email('?tolerantniy2104@gmail.com')
    func_test_send_email('!tolerantniy2104@gmail.com')
    func_test_send_email('#tolerantniy2104@gmail.com')
    func_test_send_email('tolerantniy@gmail.com')
    func_test_send_email('tole@gmail.com')
    func_test_send_email('tol@gmail.com')
    func_test_send_email('to@gmail.com')
    func_test_send_email('t@gmail.com')
    func_test_send_email('1@gmail.com')
    func_test_send_email('1@gmail.c')
    func_test_send_email('1@g.com')
    func_test_send_email('1@g.c')

