from fastapi.testclient import TestClient
from app.main import app


def test_console_served():
    response = TestClient(app).get("/")
    assert response.status_code == 200
    assert "XtreamOrchard" in response.text
    assert "Select filtered" in response.text


def test_console_uses_ingress_relative_api_urls():
    html = TestClient(app).get("/").text
    assert 'path.replace(/^\\//,"")' in html


def test_console_disables_caching_and_referrer_leakage():
    response = TestClient(app).get("/")
    assert response.headers["cache-control"] == "no-store"
    assert response.headers["referrer-policy"] == "no-referrer"
    assert response.headers["x-content-type-options"] == "nosniff"
