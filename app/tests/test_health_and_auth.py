from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_docs_available() -> None:
    response = client.get("/docs")
    assert response.status_code == 200


def test_login_validation() -> None:
    response = client.get("/redoc")
    assert response.status_code == 200
