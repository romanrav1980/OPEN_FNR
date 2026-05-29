from fastapi.testclient import TestClient
from pathlib import Path

from open_fnr_api.main import app
from open_fnr_api.supplement_governance import SOURCE_SLA_RULES


client = TestClient(app)


def test_supplement_coverage_maps_all_sections_and_documents() -> None:
    response = client.get("/supplement/coverage")

    assert response.status_code == 200
    payload = response.json()
    assert payload["supplement_document"] == "TECHNICAL_SPEC_SUPPLEMENT_1.md"
    assert len(payload["sections"]) == 13
    assert "source_sla" in payload["implemented_gates"]
    assert "TECHNICAL_SPEC.md" in payload["docs_to_sync"]


def test_source_sla_matrix_contains_required_operational_sources() -> None:
    response = client.get("/supplement/source-sla")

    assert response.status_code == 200
    payload = response.json()
    pairs = {(item["source_system"], item["dataset"]) for item in payload}

    assert len(payload) == len(SOURCE_SLA_RULES)
    assert ("POS", "sales") in pairs
    assert ("WMS", "in_transit") in pairs
    assert ("PROMO", "promo_plan_90d") in pairs
    assert ("MDM", "stores") in pairs


def test_source_sla_evaluation_blocks_degraded_publish_by_default() -> None:
    response = client.post(
        "/supplement/source-sla/evaluate",
        json={
            "source_system": "POS",
            "dataset": "sales",
            "completeness": 0.90,
            "arrived_before_cutoff": False,
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "blocked"
    assert payload["quality_flag"] == "degraded"
    assert payload["publish_allowed_by_default"] is False
    assert "data_gap" in payload["action"]


def test_ml_lifecycle_gate_matches_supplement_protocol() -> None:
    response = client.get("/supplement/ml-lifecycle")

    assert response.status_code == 200
    payload = response.json()
    assert payload["candidate_min_backtesting_weeks"] == 26
    assert payload["shadow_min_days"] == 14
    assert payload["emergency_rollback_hours"] == 1
    assert payload["fallback_chain"][-1] == "global_seasonal_naive"


def test_financial_parameters_require_business_signoff() -> None:
    response = client.get("/supplement/replenishment-financial-parameters")

    assert response.status_code == 200
    payload = response.json()
    parameters = {item["parameter"]: item for item in payload}

    assert parameters["holding_cost_rate_annual"]["owner_role"] == "CFO"
    assert parameters["service_level_targets_by_segment"]["required_before"] == "Parallel Run"


def test_api_governance_exposes_versioning_and_registry_contracts() -> None:
    response = client.get("/supplement/api-governance")

    assert response.status_code == 200
    payload = response.json()
    assert payload["version_prefix"] == "/api/v{major}/"
    assert payload["deprecation_notice_days"] == 90
    assert "error_code" in payload["standard_error_fields"]
    assert payload["consumer_registry_path"] == "docs/api-consumers/registry.md"
    assert Path(payload["consumer_registry_path"]).exists()
    assert Path(payload["error_registry_path"]).exists()


def test_supplier_isolation_requires_supplier_claim_and_audit() -> None:
    response = client.get("/supplement/supplier-isolation")

    assert response.status_code == 200
    payload = response.json()
    assert payload["supplier_api_prefix"] == "/supplier-api/v1/"
    assert payload["required_claim"] == "supplier_id"
    assert "audit_every_supplier_request" in payload["controls"]


def test_intraday_and_otb_are_out_of_scope_for_v1_with_compensating_controls() -> None:
    intraday = client.get("/supplement/scope/intraday").json()
    otb = client.get("/supplement/scope/otb").json()

    assert intraday["v1_status"] == "out_of_scope"
    assert "fresh_early_cutoff" in intraday["v1_compensating_controls"]
    assert otb["v1_status"] == "out_of_scope"
    assert "budget_aware_order_shaping" in otb["v2_requirements"]


def test_historical_simulation_is_parallel_run_prerequisite() -> None:
    response = client.get("/supplement/historical-simulation")

    assert response.status_code == 200
    payload = response.json()
    assert payload["min_weeks"] == 52
    assert payload["min_store_coverage_pct"] == 20.0
    assert payload["required_report_path"] == "docs/simulation-reports/"
    assert Path(payload["required_report_path"]).exists()


def test_notifications_human_task_sla_and_itsm_readiness_are_exposed() -> None:
    notifications = client.get("/supplement/notifications").json()
    task_slas = client.get("/supplement/human-task-sla").json()
    itsm = client.get("/supplement/itsm-readiness").json()

    assert any(item["notification_type"] == "source_sla_breach" and item["max_delivery_minutes"] == 5 for item in notifications)
    assert any(item["task_type"] == "fresh_order_review" and item["sla"] == "1 business hour" for item in task_slas)
    assert itsm["target_setting"] == "OPEN_FNR_ITSM_WEBHOOK_URL"


def test_open_questions_include_business_blockers() -> None:
    response = client.get("/supplement/open-questions")

    assert response.status_code == 200
    payload = response.json()
    question_ids = {item["question_id"] for item in payload}
    assert {"M-01", "M-07", "M-12"}.issubset(question_ids)
