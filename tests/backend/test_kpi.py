from fastapi.testclient import TestClient

from open_fnr_api.kpi import PILOT_ACCEPTANCE_METRICS, build_pilot_acceptance_pack, calculate_bias, calculate_wape, kpi_alert_required, metric_passed
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


def test_pilot_business_acceptance_pack_covers_required_business_metrics() -> None:
    response = client.get("/kpi/pilot-acceptance")
    assert response.status_code == 200

    payload = response.json()
    metrics = {item["metric"]: item for item in payload["metrics"]}

    assert payload["scope_id"] == "pilot-north-fresh-001"
    assert payload["decision"] == "accepted"
    assert payload["blockers"] == []
    assert {"wape", "service_level", "lost_sales_reduction", "overstock_reduction", "waste_reduction"}.issubset(
        metrics
    )
    assert metrics["wape"]["direction"] == "less_or_equal"
    assert metrics["service_level"]["direction"] == "greater_or_equal"
    assert "KPI formulas covered by automated tests" in payload["reproducibility_evidence"]
    assert "Business Owner" in payload["sign_off_roles"]


def test_pilot_acceptance_metric_threshold_helper_handles_direction() -> None:
    assert all(metric_passed(metric) for metric in PILOT_ACCEPTANCE_METRICS)

    bad_wape = PILOT_ACCEPTANCE_METRICS[0].model_copy(update={"value": 19.0})
    bad_service = PILOT_ACCEPTANCE_METRICS[1].model_copy(update={"value": 94.0})

    assert metric_passed(bad_wape) is False
    assert metric_passed(bad_service) is False


def test_pilot_acceptance_pack_helper_blocks_when_metric_fails(monkeypatch) -> None:
    bad_metric = PILOT_ACCEPTANCE_METRICS[0].model_copy(update={"value": 19.0, "status": "failed"})

    monkeypatch.setattr("open_fnr_api.kpi.PILOT_ACCEPTANCE_METRICS", (bad_metric, *PILOT_ACCEPTANCE_METRICS[1:]))
    pack = build_pilot_acceptance_pack()

    assert pack.decision == "blocked"
    assert pack.blockers == ("wape",)
