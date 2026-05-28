from fastapi.testclient import TestClient

from open_fnr_api.main import app
from open_fnr_api.pilot import (
    PILOT_ISSUES,
    PILOT_KPIS,
    PilotIssue,
    PilotIssueStatus,
    PilotKpi,
    pilot_ready_for_acceptance,
)


client = TestClient(app)


def test_pilot_dashboard_contains_scope_kpis_feedback_and_issues() -> None:
    response = client.get("/pilot/dashboard")
    assert response.status_code == 200

    payload = response.json()
    assert payload["scope"]["scope_id"] == "pilot-north-fresh-001"
    assert payload["scope"]["regions"] == ["north"]
    assert payload["ready_for_acceptance"] is True
    assert {kpi["name"] for kpi in payload["kpis"]} == {"wape", "service_level", "lost_sales_reduction", "overstock_reduction"}
    assert payload["feedback"][0]["status"] == "triaged"
    assert payload["issues"][0]["status"] == "accepted_risk"


def test_business_owner_can_sign_pilot_acceptance() -> None:
    response = client.post(
        "/pilot/acceptance/sign",
        json={
            "actor": "business.owner@example.org",
            "actor_role": "Business Owner",
            "decision": "Pilot accepted for expansion preparation.",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "accepted"
    assert payload["signed_by"] == "business.owner@example.org"


def test_pilot_acceptance_requires_business_owner() -> None:
    response = client.post(
        "/pilot/acceptance/sign",
        json={
            "actor": "planner@example.org",
            "actor_role": "Forecast Planner",
            "decision": "not allowed",
        },
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "only Business Owner can sign pilot acceptance"


def test_pilot_acceptance_helper_blocks_bad_kpi_or_critical_issue() -> None:
    bad_kpis = (
        PilotKpi(name="wape", value=19.1, threshold=18.0, unit="%", status="red"),
        PilotKpi(name="service_level", value=96.1, threshold=95.0, unit="%", status="green"),
    )
    critical_issues = (
        PilotIssue(
            issue_id="critical-1",
            severity="critical",
            status=PilotIssueStatus.OPEN,
            owner_role="Product Owner",
            summary="blocking issue",
            sla_due_at="2026-05-29T12:00:00Z",
        ),
    )

    assert pilot_ready_for_acceptance(PILOT_KPIS, PILOT_ISSUES) is True
    assert pilot_ready_for_acceptance(bad_kpis, PILOT_ISSUES) is False
    assert pilot_ready_for_acceptance(PILOT_KPIS, critical_issues) is False
