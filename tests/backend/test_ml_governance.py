from fastapi.testclient import TestClient

from open_fnr_api.main import app
from open_fnr_api.ml_governance import (
    DriftSeverity,
    MODEL_CANDIDATES,
    ModelCandidate,
    ModelReleaseStatus,
    model_release_gate,
)


client = TestClient(app)


def test_model_candidates_show_shadow_metrics_and_drift() -> None:
    response = client.get("/ml-governance/candidates")
    assert response.status_code == 200

    candidate = response.json()["items"][0]
    assert candidate["model_id"] == "regular-demand-lgbm-v2"
    assert candidate["wape"] == 14.9
    assert candidate["baseline_wape"] == 18.4
    assert candidate["shadow_wape"] == 15.2
    assert candidate["drift_severity"] == "low"


def test_model_release_gate_allows_good_candidate() -> None:
    response = client.get("/ml-governance/candidates/regular-demand-lgbm-v2/gate")
    assert response.status_code == 200
    assert response.json()["release_allowed"] is True


def test_forecast_owner_can_approve_and_release_model_with_audit() -> None:
    response = client.post(
        "/ml-governance/candidates/regular-demand-lgbm-v2/approve",
        json={
            "actor": "forecast.owner@example.org",
            "actor_role": "Forecast Owner",
            "reason": "Backtesting, drift and shadow run accepted.",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["model"]["status"] == "approved"
    assert payload["audit_event"]["event_type"] == "model_approve"


def test_model_release_requires_forecast_owner() -> None:
    response = client.post(
        "/ml-governance/candidates/regular-demand-lgbm-v2/release",
        json={
            "actor": "scientist@example.org",
            "actor_role": "Data Scientist",
            "reason": "not allowed",
        },
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Forecast Owner role required"


def test_data_scientist_can_trigger_rollback_with_audit() -> None:
    response = client.post(
        "/ml-governance/candidates/regular-demand-lgbm-v2/rollback",
        json={
            "actor": "scientist@example.org",
            "actor_role": "Data Scientist",
            "reason": "Rollback rehearsal after drift alert.",
        },
    )

    assert response.status_code == 200
    assert response.json()["model"]["status"] == "rolled_back"


def test_model_release_gate_blocks_high_drift_or_bad_bias() -> None:
    good = MODEL_CANDIDATES[0]
    high_drift = good.model_copy(update={"drift_severity": DriftSeverity.HIGH})
    bad_bias = good.model_copy(update={"bias": 3.1})
    worse_than_baseline = ModelCandidate(
        model_id="bad",
        version="1",
        algorithm="LightGBM",
        training_snapshot_id="snapshot",
        wape=19.0,
        bias=0.1,
        baseline_wape=18.4,
        shadow_wape=19.1,
        drift_severity=DriftSeverity.LOW,
        status=ModelReleaseStatus.CANDIDATE,
    )

    assert model_release_gate(good) is True
    assert model_release_gate(high_drift) is False
    assert model_release_gate(bad_bias) is False
    assert model_release_gate(worse_than_baseline) is False
