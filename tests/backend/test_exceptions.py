from fastapi.testclient import TestClient

from open_fnr_api import exceptions
from open_fnr_api.exceptions import ExceptionSeverity, ExceptionType, decide_exception_severity, route_exception_owner
from open_fnr_api.main import app


client = TestClient(app)


class CapturingOperationalDecisionRepository:
    mode = "in_memory"

    def __init__(self) -> None:
        self.decisions = []

    def upsert_decision(self, decision):
        self.decisions.append(decision)
        return decision


def test_exception_center_lists_linked_business_objects() -> None:
    response = client.get("/exceptions")
    assert response.status_code == 200

    payload = response.json()
    assert payload["total"] == 4
    stockout = payload["items"][0]
    assert stockout["exception_type"] == "stock_out_risk"
    assert stockout["owner_role"] == "Replenishment Planner"
    assert stockout["linked_objects"][0]["object_id"] == "projection-20260528-s001-sku001"


def test_exception_filters_by_type_severity_and_owner() -> None:
    response = client.get(
        "/exceptions",
        params={
            "exception_type": "promo_shortage_risk",
            "severity": "critical",
            "owner_role": "Supply Chain Manager",
        },
    )
    assert response.status_code == 200

    payload = response.json()
    assert payload["total"] == 1
    assert payload["items"][0]["exception_id"] == "exc-promo-shortage-20260528-001"


def test_exception_take_resolve_ignore_escalate_actions_are_audited() -> None:
    response = client.post(
        "/exceptions/exc-stockout-20260528-001/actions",
        json={
            "actor": "replenishment.planner@example.org",
            "actor_role": "Replenishment Planner",
            "action": "resolve",
            "reason": "order adjusted",
            "comment": "Raised final order and stock-out risk is removed.",
        },
    )
    assert response.status_code == 200

    payload = response.json()
    assert payload["exception"]["status"] == "resolved"
    assert payload["exception"]["owner_user"] == "replenishment.planner@example.org"
    assert payload["audit_event"]["action"] == "resolve"


def test_exception_action_writes_operational_decision_boundary(monkeypatch) -> None:
    repository = CapturingOperationalDecisionRepository()
    monkeypatch.setattr(exceptions, "operational_decision_repository", repository)

    response = client.post(
        "/exceptions/exc-stockout-20260528-001/actions",
        json={
            "actor": "replenishment.planner@example.org",
            "actor_role": "Replenishment Planner",
            "action": "resolve",
            "reason": "order adjusted",
            "comment": "Repository boundary check.",
        },
    )

    assert response.status_code == 200
    assert repository.decisions[0].decision_type == "exception_action"
    assert repository.decisions[0].object_id == "exc-stockout-20260528-001"
    assert repository.decisions[0].status == "resolved"
    assert repository.decisions[0].payload["exception_type"] == "stock_out_risk"


def test_exception_action_rejects_wrong_role() -> None:
    response = client.post(
        "/exceptions/exc-dq-20260528-001/actions",
        json={
            "actor": "viewer@example.org",
            "actor_role": "Viewer",
            "action": "resolve",
            "reason": "not allowed",
            "comment": "Should fail.",
        },
    )
    assert response.status_code == 403


def test_exception_routing_and_severity_decisions() -> None:
    assert route_exception_owner(ExceptionType.DATA_QUALITY) == "Data Owner"
    assert route_exception_owner(ExceptionType.FORECAST_ANOMALY) == "Forecast Planner"
    assert decide_exception_severity(ExceptionType.STOCK_OUT_RISK, impact_qty=500) == ExceptionSeverity.HIGH
    assert decide_exception_severity(ExceptionType.PROMO_SHORTAGE_RISK, impact_qty=1) == ExceptionSeverity.CRITICAL
