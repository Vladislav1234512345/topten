# from fastapi.testclient import TestClient
#
# from src.v1.jwt import router
# from src.container import logger
#
#
# client = TestClient(router)
#
#
# def test_refresh_tokens():
#     client.cookies.set(
#         name="refresh_token",
#         value="eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0eXBlIjoicmVmcmVzaCIsInVpZCI6MSwic3ViIjoiYW50b25rdXRvcm92QGdtYWlsLmNvbSIsIm5hbWUiOiJWbGFkaXNsYXYiLCJpYXQiOjE3MzYxOTgyOTUsImV4cCI6MTczNjgwMzA5NX0.AQuM8LNLE-EKzfMCstOZ3gUUztpZV1mbqHkTHPlhJw0N_e9spefKVlYLVAXDeBJNmuDJXEm6QQtYw40yaOffnmBIpiKkhRhOSuF5qQ8wfrwJat2fmO7MpNm12zfcFxST5OCtVGhQPptkPytFMP5Y6hXd1tfltE2D2QqirHVGGgCHNwcVs7G7ybHa-7qnT_4ZO4fYkwVJ7wFqtT9RjnMCsqRQ6z2d3Xlcp-wfXhPBBt5FlTErfhn3AQgJBkOz1g4VLvBvYbNOj0rKiuEIgeK8RQis85r9mf95fwOe0Z8bs7phtDMIrqPkp9Ucx5buEoOXjnjpxZWahsLGFiUYN9jyQw",
#     )
#     response = client.post("/jwt/refresh")
#     logger.info(response.url)
#     assert response.status_code == 200
#     assert response.json() == {"message": "Токены успешно обновлены."}
#
#     logger.info(f"cookies:\n{response.cookies}")
#     logger.info(f"headers:\n{response.headers}")
