from fastapi.testclient import TestClient

from open_fnr_api.main import app


client = TestClient(app)


def test_champion_challenger_registry_exposes_shadow_mode() -> None:
    response = client.get("/ml-governance/registry")
    assert response.status_code == 200
    payload = response.json()

    entry = payload["items"][0]
    assert entry["model_family"] == "regular_demand"
    assert entry["champion_model_id"] == "seasonal-naive-v1"
    assert entry["challenger_model_id"] == "regular-demand-lgbm-v2"
    assert entry["traffic_mode"] == "shadow_only"
    assert entry["challenger_wape"] < entry["champion_wape"]


def test_shadow_scoring_report_requires_minimum_shadow_period() -> None:
    response = client.get("/ml-governance/shadow-reports")
    assert response.status_code == 200
    report = response.json()["items"][0]

    assert report["shadow_days_completed"] >= report["min_shadow_days_required"]
    assert report["status"] == "passed"
    assert report["shadow_wape"] <= report["production_wape"]


def test_drift_report_exposes_severity_and_action() -> None:
    response = client.get("/ml-governance/drift-reports")
    assert response.status_code == 200
    report = response.json()["items"][0]

    assert report["severity"] == "low"
    assert report["feature_drift_score"] < 0.1
    assert report["recommended_action"] == "continue_shadow_and_prepare_release_review"


def test_fallback_plan_exposes_rollback_rehearsal() -> None:
    response = client.get("/ml-governance/fallback-plans")
    assert response.status_code == 200
    plan = response.json()["items"][0]

    assert plan["fallback_model_id"] == "seasonal-naive-v1"
    assert plan["rehearsal_status"] == "passed"
    assert plan["max_rollback_minutes"] <= 15
