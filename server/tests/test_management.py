import asyncio
import os
from fastapi.testclient import TestClient
from app import main


def test_management_requires_token(monkeypatch, tmp_path):
    monkeypatch.setattr(main, "DB", tmp_path / "catalog.db")
    monkeypatch.setenv("XTREAM_ORCHARD_ADMIN_TOKEN", "test-secret")
    client = TestClient(main.app)
    assert client.get("/api/v1/channels").status_code == 401
    assert client.get("/api/v1/channels", headers={"Authorization": "Bearer wrong"}).status_code == 401
    headers = {"Authorization": "Bearer test-secret"}
    assert client.post("/api/v1/channels/import", json=[
        {"id": "10", "name": "Local News", "category": "News"}
    ], headers=headers).status_code == 200
    assert client.get("/api/v1/config", headers=headers).json()["channels"] == []
    assert client.patch("/api/v1/channels/10/visibility", json={"visible": True}, headers=headers).status_code == 200
    assert client.get("/api/v1/config", headers=headers).json()["channels"][0]["id"] == "10"
    # Catalog refresh must preserve user visibility.
    assert client.post("/api/v1/channels/import", json=[
        {"id": "10", "name": "Renamed News", "category": "News"},
        {"id": "11", "name": "New Channel"}
    ], headers=headers).status_code == 200
    snapshot = client.get("/api/v1/config", headers=headers).json()
    assert len(snapshot["channels"]) == 1
    assert snapshot["channels"][0]["name"] == "Renamed News"


def test_missing_provider_config(monkeypatch):
    monkeypatch.setenv("XTREAM_ORCHARD_ADMIN_TOKEN", "test-secret")
    for key in ("XTREAM_ORCHARD_PROVIDER_URL", "XTREAM_ORCHARD_PROVIDER_USERNAME", "XTREAM_ORCHARD_PROVIDER_PASSWORD"):
        monkeypatch.delenv(key, raising=False)
    client = TestClient(main.app)
    assert client.post("/api/v1/providers/xtream/refresh", headers={
        "Authorization": "Bearer test-secret"
    }).status_code == 503
