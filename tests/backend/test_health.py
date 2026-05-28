from fastapi.testclient import TestClient

from open_fnr_api.main import app


client = TestClient(app)


def test_health_endpoint() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_metadata_endpoint_lists_core_modules() -> None:
    response = client.get("/metadata")
    assert response.status_code == 200
    payload = response.json()
    assert payload["name"] == "OPEN FNR API"
    assert "forecasting" in payload["modules"]
    assert "replenishment" in payload["modules"]
    assert "process-engine" in payload["modules"]
    assert "daily-pipeline" in payload["modules"]
