from fastapi.testclient import TestClient

from open_fnr_api.forecast import calculate_bias, calculate_wape
from open_fnr_api.main import app


client = TestClient(app)


def test_wape_formula() -> None:
    assert calculate_wape([100, 50], [90, 60]) == 20 / 150


def test_bias_formula() -> None:
    assert round(calculate_bias([100, 50], [90, 60]), 6) == 0


def test_latest_forecast_version_endpoint() -> None:
    response = client.get("/forecast/versions/latest")
    assert response.status_code == 200

    payload = response.json()
    assert payload["forecast_version"] == "regular-baseline-20260528-001"
    assert payload["status"] == "published"
    assert payload["wape"] == 0.184


def test_forecast_rows_endpoint() -> None:
    response = client.get("/forecast/versions/regular-baseline-20260528-001/rows")
    assert response.status_code == 200
    assert response.json()["total"] == 2


def test_forecast_rows_unknown_version_returns_404() -> None:
    response = client.get("/forecast/versions/missing/rows")
    assert response.status_code == 404


def test_forecast_workbench_filters_by_sku() -> None:
    response = client.get("/forecast/workbench", params={"sku_id": "SKU001"})
    assert response.status_code == 200

    payload = response.json()
    assert payload["total"] == 1
    assert payload["items"][0]["sku_id"] == "SKU001"
    assert payload["summary"]["total_rows"] == 1


def test_forecast_workbench_empty_state() -> None:
    response = client.get("/forecast/workbench", params={"store_id": "missing"})
    assert response.status_code == 200

    payload = response.json()
    assert payload["total"] == 0
    assert payload["items"] == []
