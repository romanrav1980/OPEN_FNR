from fastapi.testclient import TestClient

from open_fnr_api.main import app
from open_fnr_api.pilot import (
    PILOT_ISSUES,
    PILOT_KPIS,
    PilotIssue,
    PilotIssueStatus,
    PilotKpi,
    build_pilot_readiness_pack,
    build_pilot_shadow_pack,
    build_shadow_mode_summary,
    pilot_ready_for_acceptance,
)


client = TestClient(app)


def test_pilot_dashboard_contains_scope_kpis_feedback_and_issues() -> None:
    response = client.get("/pilot/dashboard")
    assert response.status_code == 200

    payload = response.json()
    assert payload["scope"]["scope_id"] == "pilot-north-fresh-001"
    assert payload["scope"]["regions"] == ["north"]
    assert payload["scope"]["store_count"] == 3
    assert payload["scope"]["sku_count"] == 1200
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


def test_pilot_shadow_pack_contains_scope_runbook_and_rollback() -> None:
    response = client.get("/pilot/shadow-pack")
    assert response.status_code == 200

    payload = response.json()
    assert payload["pack_id"] == "pilot-shadow-pack-north-fresh-001"
    assert payload["mode"] == "shadow"
    assert payload["ready_for_shadow"] is True
    assert len(payload["checklist"]) == 4
    assert len(payload["runbook"]) == 5
    assert {item["trigger"] for item in payload["rollback"]} == {
        "critical_data_gap",
        "wape_above_threshold",
        "export_incident",
    }


def test_pilot_shadow_pack_helper_is_ready_when_all_checklist_items_ready() -> None:
    pack = build_pilot_shadow_pack()

    assert pack.ready_for_shadow is True
    assert pack.scope.scope_id == "pilot-north-fresh-001"
    assert pack.runbook[0].owner_role == "Data Engineer"


def test_pilot_readiness_pack_freezes_scope_data_calendar_and_thresholds() -> None:
    response = client.get("/pilot/readiness-pack")
    assert response.status_code == 200

    payload = response.json()
    readiness_areas = {item["area"] for item in payload["data_readiness"]}
    threshold_metrics = {item["metric"] for item in payload["thresholds"]}

    assert payload["scope"]["suppliers"] == ["SUP-FRESH-01", "SUP-GROCERY-02"]
    assert payload["signoff"]["status"] == "signed"
    assert payload["signoff"]["pending_roles"] == []
    assert payload["ready_for_shadow_mode"] is True
    assert {"sales_history", "stock_and_in_transit", "active_matrix", "promo_history"}.issubset(readiness_areas)
    assert {"wape", "service_level", "lost_sales_reduction", "overstock_reduction", "waste_reduction"}.issubset(
        threshold_metrics
    )
    assert payload["business_calendar"][0]["day_type"] == "pilot_start"


def test_pilot_data_readiness_requires_at_least_twelve_months_when_history_is_applicable() -> None:
    pack = build_pilot_readiness_pack()

    assert pack.ready_for_shadow_mode is True
    assert all(item.blocker_count == 0 for item in pack.data_readiness)
    assert all(item.history_months is None or item.history_months >= 12 for item in pack.data_readiness)


def test_pilot_scope_signoff_endpoint_records_all_required_roles() -> None:
    response = client.get("/pilot/scope-signoff")
    assert response.status_code == 200

    payload = response.json()

    assert payload["scope_id"] == "pilot-north-fresh-001"
    assert set(payload["signed_roles"]) == {"Business Owner", "Supply Chain Director", "Data Platform Lead", "IT Ops"}
    assert payload["status"] == "signed"


def test_shadow_mode_summary_keeps_exports_disabled_and_compares_legacy_orders() -> None:
    response = client.get("/pilot/shadow-runs")
    assert response.status_code == 200

    payload = response.json()
    run = payload["runs"][0]
    metric_names = {item["metric"] for item in run["metrics"]}

    assert payload["mode"] == "shadow"
    assert payload["export_enabled"] is False
    assert payload["ready_for_business_review"] is True
    assert run["compared_orders"] > 0
    assert run["export_enabled"] is False
    assert {"wape", "bias", "service_level_proxy", "order_quantity_delta_abs"}.issubset(metric_names)
    assert run["exceptions"][0]["owner_role"] == "Replenishment Owner"


def test_shadow_run_detail_supports_planner_review_actions() -> None:
    response = client.get("/pilot/shadow-runs/shadow-run-20260601-001")
    assert response.status_code == 200

    payload = response.json()

    assert payload["status"] == "business_review"
    assert "review amber order deltas" in payload["planner_actions"]
    assert payload["exceptions"][0]["recommended_action"] == "planner review before controlled export gate"


def test_shadow_run_detail_returns_not_found_for_unknown_run() -> None:
    response = client.get("/pilot/shadow-runs/unknown")

    assert response.status_code == 404
    assert response.json()["detail"] == "shadow run not found"


def test_shadow_mode_summary_helper_counts_metric_statuses() -> None:
    summary = build_shadow_mode_summary()

    assert summary["export_enabled"] is False
    assert summary["green_metric_count"] == 3
    assert summary["amber_metric_count"] == 1


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
