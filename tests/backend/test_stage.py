from fastapi.testclient import TestClient

from open_fnr_api.main import app
from open_fnr_api.stage import STAGE_STEPS, StageStep, StageStepStatus, is_stage_go_no_go_ready


client = TestClient(app)


def test_stage_run_contains_full_daily_cycle_and_go_no_go_status() -> None:
    response = client.get("/stage/runs")
    assert response.status_code == 200

    run = response.json()["items"][0]
    assert run["status"] == "go_no_go_ready"
    assert run["snapshot_id"] == "stage-snapshot-20260528-001"
    assert [step["key"] for step in run["steps"]] == ["dq", "forecast", "promo", "replenishment", "exceptions", "publication"]
    assert run["critical_defects"] == 0
    assert run["accepted_risks"] == 2


def test_stage_trace_preserves_process_order_and_evidence() -> None:
    response = client.get("/stage/runs/stage-run-20260528-001/trace")
    assert response.status_code == 200

    trace = response.json()["trace"]
    assert [item["order"] for item in trace] == [1, 2, 3, 4, 5, 6]
    assert trace[0]["evidence"] == "DQ blockers = 0"
    assert trace[-1]["key"] == "publication"


def test_stage_uat_checklist_covers_pilot_roles() -> None:
    response = client.get("/stage/runs/stage-run-20260528-001")
    assert response.status_code == 200

    roles = {item["role"] for item in response.json()["uat_checklist"]}
    assert {"Data Owner", "Forecast Planner", "Supply Chain Manager", "Integration Engineer"}.issubset(roles)


def test_stage_go_no_go_rejects_failed_step_or_critical_defect() -> None:
    failed_steps = (
        StageStep(order=1, key="dq", name="DQ checks", owner_role="Data Engineer", status=StageStepStatus.FAILED, evidence="blocker"),
    )

    assert is_stage_go_no_go_ready(STAGE_STEPS, critical_defects=0) is True
    assert is_stage_go_no_go_ready(STAGE_STEPS, critical_defects=1) is False
    assert is_stage_go_no_go_ready(failed_steps, critical_defects=0) is False
