from fastapi.testclient import TestClient

from open_fnr_api import adjustments
from open_fnr_api.adjustments import AdjustmentMode, adjustment_approval_required, preview_adjusted_value
from open_fnr_api.main import app


client = TestClient(app)


class CapturingOperationalDecisionRepository:
    mode = "in_memory"

    def __init__(self) -> None:
        self.decisions = []

    def upsert_decision(self, decision):
        self.decisions.append(decision)
        return decision


def test_adjustments_are_listed_without_overwriting_targets() -> None:
    response = client.get("/adjustments")
    assert response.status_code == 200

    payload = response.json()
    assert payload["total"] == 2
    assert payload["items"][0]["target_id"] == "regular-baseline-20260528-001"
    assert payload["items"][0]["status"] == "previewed"


def test_adjustment_preview_shows_impact_and_approval_requirement() -> None:
    response = client.get("/adjustments/adj-forecast-20260528-001/preview", params={"base_value": 120})
    assert response.status_code == 200

    payload = response.json()
    assert payload["base_value"] == 120
    assert payload["adjusted_value"] == 132
    assert payload["delta_value"] == 12
    assert payload["affected_rows"] == 4
    assert payload["approval_required"] is True


def test_adjustment_apply_returns_status_and_audit() -> None:
    response = client.post(
        "/adjustments/adj-forecast-20260528-001/apply",
        json={
            "actor": "forecast.planner@example.org",
            "actor_role": "Forecast Planner",
            "comment": "Apply before publication cutoff.",
        },
    )
    assert response.status_code == 200

    payload = response.json()
    assert payload["adjustment"]["status"] == "applied"
    assert payload["audit_event"]["old_status"] == "previewed"
    assert payload["audit_event"]["new_status"] == "applied"


def test_adjustment_action_writes_operational_decision_boundary(monkeypatch) -> None:
    repository = CapturingOperationalDecisionRepository()
    monkeypatch.setattr(adjustments, "operational_decision_repository", repository)

    response = client.post(
        "/adjustments/adj-forecast-20260528-001/apply",
        json={
            "actor": "forecast.planner@example.org",
            "actor_role": "Forecast Planner",
            "comment": "Repository boundary check.",
        },
    )

    assert response.status_code == 200
    assert repository.decisions[0].decision_type == "manual_adjustment_action"
    assert repository.decisions[0].object_id == "adj-forecast-20260528-001"
    assert repository.decisions[0].status == "applied"
    assert repository.decisions[0].payload["target_type"] == "forecast"


def test_wrong_role_cannot_manage_adjustment() -> None:
    response = client.post(
        "/adjustments/adj-forecast-20260528-001/cancel",
        json={
            "actor": "viewer@example.org",
            "actor_role": "Viewer",
            "comment": "Not allowed.",
        },
    )
    assert response.status_code == 403


def test_adjustment_helpers() -> None:
    assert preview_adjusted_value(120, AdjustmentMode.PERCENT, 10) == 132
    assert preview_adjusted_value(120, AdjustmentMode.ABSOLUTE, 150) == 150
    assert adjustment_approval_required(AdjustmentMode.PERCENT, 10, "Forecast Planner") is True
    assert adjustment_approval_required(AdjustmentMode.PERCENT, 3, "Forecast Planner") is False
