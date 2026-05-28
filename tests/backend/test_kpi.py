from fastapi.testclient import TestClient

from open_fnr_api.kpi import calculate_bias, calculate_wape, kpi_alert_required
from open_fnr_api.main import app


client = TestClient(app)


def test_kpi_dashboard_exposes_accuracy_and_business_value() -> None:
    response = client.get("/kpi/dashboard")
    assert response.status_code == 200

    payload = response.json()
    assert payload["filters"]["regions"] == ["all", "north"]
    assert payload["items"][0]["wape"] == 0.158
    assert payload["items"][0]["proposal_acceptance_rate"] == 0.87
    assert "total_business_value" in payload["business_value"]


def test_kpi_dashboard_drill_down_to_sku() -> None:
    response = client.get("/kpi/dashboard", params={"store_id": "S001", "sku_id": "SKU001"})
    assert response.status_code == 200

    payload = response.json()
    assert len(payload["items"]) == 1
    assert payload["items"][0]["segment_id"] == "sku-s001-sku001"
    assert payload["items"][0]["status"] == "action_created"


def test_kpi_segment_endpoint_returns_review_required_segment() -> None:
    response = client.get("/kpi/segments/region-north-fresh")
    assert response.status_code == 200

    payload = response.json()
    assert payload["status"] == "review_required"
    assert payload["service_level"] == 0.918


def test_kpi_formulas_match_golden_dataset() -> None:
    actual = [100, 200, 300]
    forecast = [90, 220, 330]

    assert round(calculate_wape(actual, forecast), 4) == 0.1
    assert round(calculate_bias(actual, forecast), 4) == 0.0667


def test_kpi_alert_decision_thresholds() -> None:
    assert kpi_alert_required(wape=0.21, bias=0.01, service_level=0.96) is True
    assert kpi_alert_required(wape=0.1, bias=0.07, service_level=0.96) is True
    assert kpi_alert_required(wape=0.1, bias=0.01, service_level=0.91) is True
    assert kpi_alert_required(wape=0.1, bias=0.01, service_level=0.96) is False
