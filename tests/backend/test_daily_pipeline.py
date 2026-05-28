from datetime import date

from fastapi.testclient import TestClient

from open_fnr_api.daily_pipeline import DailyPipelineGateRequest, run_daily_pipeline_gate
from open_fnr_api.main import app
from open_fnr_api.pilot_fixtures import generate_pilot_landing_pack


client = TestClient(app)


def test_daily_pipeline_gate_blocks_when_sources_are_missing(tmp_path) -> None:
    request = DailyPipelineGateRequest(
        business_date=date(2026, 5, 28),
        actor="data.platform.owner@example.org",
        landing_root_path=str(tmp_path),
    )
    response = run_daily_pipeline_gate(request)

    assert response.status == "blocked"
    assert response.stages[0].stage_key == "shadow_load"
    assert response.stages[0].status == "blocked"
    assert response.stages[-1].status == "skipped"


def test_daily_pipeline_gate_reaches_feature_build_with_pilot_pack(tmp_path) -> None:
    generate_pilot_landing_pack(tmp_path, date(2026, 5, 28))
    request = DailyPipelineGateRequest(
        business_date=date(2026, 5, 28),
        actor="data.platform.owner@example.org",
        landing_root_path=str(tmp_path),
    )
    response = run_daily_pipeline_gate(request)

    assert response.status == "ready_for_feature_build"
    assert [stage.stage_key for stage in response.stages] == [
        "shadow_load",
        "source_contract_dq",
        "clean_publication",
        "feature_build",
    ]
    assert response.stages[-1].task_id == "task-feature-build-001"
    assert response.audit_recorded is True


def test_daily_pipeline_gate_api_returns_stage_details(tmp_path) -> None:
    generate_pilot_landing_pack(tmp_path, date(2026, 5, 28))
    response = client.post(
        "/pipeline/daily-gate/run",
        json={
            "business_date": "2026-05-28",
            "actor": "data.platform.owner@example.org",
            "landing_root_path": str(tmp_path),
        },
    )
    assert response.status_code == 200

    payload = response.json()
    assert payload["status"] == "ready_for_feature_build"
    assert payload["stages"][2]["stage_key"] == "clean_publication"
    assert payload["stages"][3]["process_key"] == "feature_build_process"
