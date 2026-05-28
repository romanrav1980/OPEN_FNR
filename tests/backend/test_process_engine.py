from fastapi.testclient import TestClient

from open_fnr_api.main import app


client = TestClient(app)


def test_process_definitions_include_bpmn_dmn_cmmn() -> None:
    response = client.get("/process/definitions")
    assert response.status_code == 200

    payload = response.json()
    artifact_types = {item["artifact_type"] for item in payload["items"]}
    assert {"bpmn", "dmn", "cmmn"}.issubset(artifact_types)
    assert any(item["key"] == "forecast_review_process" for item in payload["items"])
    assert any(item["key"] == "dc_replenishment_process" for item in payload["items"])
    assert any(item["key"] == "dc_allocation_priority_decision" for item in payload["items"])
    assert any(item["key"] == "dc_shortage_case" for item in payload["items"])
    assert any(item["key"] == "performance_test_run_process" for item in payload["items"])
    assert any(item["key"] == "performance_gate_decision" for item in payload["items"])
    assert any(item["key"] == "performance_regression_case" for item in payload["items"])
    assert any(item["key"] == "access_request_process" for item in payload["items"])
    assert any(item["key"] == "role_assignment_decision" for item in payload["items"])
    assert any(item["key"] == "security_incident_case" for item in payload["items"])
    assert any(item["key"] == "stage_daily_cycle_process" for item in payload["items"])
    assert any(item["key"] == "stage_go_no_go_decision" for item in payload["items"])
    assert any(item["key"] == "stage_uat_case" for item in payload["items"])
    assert any(item["key"] == "pilot_operational_process" for item in payload["items"])
    assert any(item["key"] == "pilot_acceptance_decision" for item in payload["items"])
    assert any(item["key"] == "pilot_exception_case" for item in payload["items"])
    assert any(item["key"] == "industrial_data_load_process" for item in payload["items"])
    assert any(item["key"] == "industrial_dq_gate_decision" for item in payload["items"])
    assert any(item["key"] == "large_scale_data_incident_case" for item in payload["items"])
    assert any(item["key"] == "model_release_process" for item in payload["items"])
    assert any(item["key"] == "model_release_gate_decision" for item in payload["items"])
    assert any(item["key"] == "model_drift_case" for item in payload["items"])
    assert any(item["key"] == "industrial_replenishment_process" for item in payload["items"])
    assert any(item["key"] == "bulk_auto_approval_decision" for item in payload["items"])
    assert any(item["key"] == "replenishment_scale_exception_case" for item in payload["items"])
    assert any(item["key"] == "process_change_management_process" for item in payload["items"])
    assert any(item["key"] == "process_change_risk_decision" for item in payload["items"])
    assert any(item["key"] == "process_incident_case" for item in payload["items"])
    assert any(item["key"] == "incident_management_process" for item in payload["items"])
    assert any(item["key"] == "incident_severity_decision" for item in payload["items"])
    assert any(item["key"] == "production_incident_case" for item in payload["items"])
    assert any(item["key"] == "release_go_no_go_process" for item in payload["items"])
    assert any(item["key"] == "release_readiness_decision" for item in payload["items"])
    assert any(item["key"] == "release_risk_case" for item in payload["items"])
    assert any(item["key"] == "purchase_proposal_process" for item in payload["items"])
    assert any(item["key"] == "supplier_selection_decision" for item in payload["items"])
    assert any(item["key"] == "supplier_share_exception_decision" for item in payload["items"])
    assert any(item["key"] == "supplier_constraint_case" for item in payload["items"])
    assert any(item["key"] == "shelf_space_review_process" for item in payload["items"])
    assert any(item["key"] == "display_capacity_decision" for item in payload["items"])
    assert any(item["key"] == "direct_to_shelf_decision" for item in payload["items"])
    assert any(item["key"] == "shelf_capacity_exception_case" for item in payload["items"])
    assert any(item["key"] == "capacity_smoothing_process" for item in payload["items"])
    assert any(item["key"] == "capacity_overload_decision" for item in payload["items"])
    assert any(item["key"] == "order_shift_priority_decision" for item in payload["items"])
    assert any(item["key"] == "capacity_overload_case" for item in payload["items"])


def test_task_inbox_filters_by_candidate_role() -> None:
    response = client.get("/process/tasks", params={"role": "Promo Planner"})
    assert response.status_code == 200

    tasks = response.json()["items"]
    assert len(tasks) == 1
    assert tasks[0]["task_id"] == "task-promo-001"
    assert "complete" in tasks[0]["available_actions"]


def test_task_completion_returns_audit_events() -> None:
    response = client.post(
        "/process/tasks/task-promo-001/complete",
        json={
            "action": "complete",
            "actor": "promo.planner@example.org",
            "comment": "Fixed display capacity and promo price.",
        },
    )
    assert response.status_code == 200

    payload = response.json()
    assert payload["task"]["status"] == "completed"
    assert [event["event_type"] for event in payload["audit_events"]] == ["comment_added", "task_completed"]


def test_task_completion_rejects_unavailable_action() -> None:
    response = client.post(
        "/process/tasks/task-promo-001/complete",
        json={
            "action": "approve",
            "actor": "promo.planner@example.org",
            "comment": "Trying a wrong transition.",
        },
    )
    assert response.status_code == 400


def test_task_completion_rejects_wrong_actor_role() -> None:
    response = client.post(
        "/process/tasks/task-promo-approval-category-001/complete",
        json={
            "action": "approve",
            "actor": "promo.planner@example.org",
            "actor_role": "Promo Planner",
            "comment": "Trying to approve outside assigned role.",
        },
    )
    assert response.status_code == 403


def test_category_manager_can_approve_category_task() -> None:
    response = client.post(
        "/process/tasks/task-promo-approval-category-001/complete",
        json={
            "action": "approve",
            "actor": "category.manager@example.org",
            "actor_role": "Category Manager",
            "comment": "Commercial terms approved.",
        },
    )
    assert response.status_code == 200

    payload = response.json()
    assert payload["task"]["status"] == "completed"
    assert payload["audit_events"][1]["event_type"] == "task_completed"


def test_process_audit_endpoint_returns_instance_history() -> None:
    response = client.get("/process/instances/proc-promo-20260601-001/audit")
    assert response.status_code == 200

    events = response.json()["items"]
    assert events[0]["event_type"] == "process_started"
    assert events[1]["event_type"] == "task_created"
