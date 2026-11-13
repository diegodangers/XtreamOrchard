from fastapi.testclient import TestClient
from app.main import app


def test_console_served():
    response = TestClient(app).get("/")
    assert response.status_code == 200
    assert "XtreamOrchard" in response.text
    assert "Select filtered" in response.text
