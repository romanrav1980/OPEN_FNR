from datetime import date

from fastapi.testclient import TestClient

from open_fnr_api.integration_operations import (
    build_reconciliation_summary,
    build_retry_plan,
    build_source_readiness,
)
from open_fnr_api.main import app
from open_fnr_api.pilot_fixtures import generate_pilot_landing_pack


client = TestClient(app)


def test_source_readiness_blocks_when_sources_are_missing(tmp_path) -> None:
    readiness = build_source_readiness(date(2026, 5, 28), str(tmp_path))

    assert readiness.status == "blocked"
    assert readiness.total_contracts == 11
    assert readiness.blocked_contracts == 11
    assert readiness.ready_contracts == 0
    assert all(item.retry_allowed for item in readiness.items)


def test_source_readiness_is_ready_for_complete_pilot_pack(tmp_path) -> None:
    generate_pilot_landing_pack(tmp_path, date(2026, 5, 28))

    response = client.get(
        "/integration/operations/source-readiness",
        params={"business_date": "2026-05-28", "landing_root_path": str(tmp_path)},
    )
    assert response.status_code == 200

    payload = response.json()
    assert payload["status"] == "ready"
    assert payload["total_contracts"] == 11
    assert payload["blocked_contracts"] == 0
    assert any(item["contract_name"] == "erp_supplier_term_line" for item in payload["items"])
    assert any(item["contract_name"] == "dwh_sales_history_line" for item in payload["items"])


def test_retry_plan_uses_idempotency_keys_for_blocked_sources(tmp_path) -> None:
    retry_plan = build_retry_plan(date(2026, 5, 28), str(tmp_path))

    assert retry_plan.total == 11
    assert all(item.retry_strategy == "same_idempotency_key_no_duplicate_clean_rows" for item in retry_plan.items)
    assert all(item.max_attempts == 3 for item in retry_plan.items)
    assert any(item.idempotency_key.startswith("DWH:dwh_sales_history_line") for item in retry_plan.items)


def test_reconciliation_summary_exposes_keys_and_downstream_blockers(tmp_path) -> None:
    summary = build_reconciliation_summary(date(2026, 5, 28), str(tmp_path))

    assert summary.status == "blocked"
    assert summary.total == 11
    assert summary.blocked_count == 11
    supplier_terms = next(item for item in summary.items if item.contract_name == "erp_supplier_term_line")
    assert supplier_terms.reconciliation_keys == ("supplier_id", "sku_id", "location_scope", "valid_from")
    assert "replenishment" in supplier_terms.downstream_blockers


def test_reconciliation_api_is_ready_for_complete_pilot_pack(tmp_path) -> None:
    generate_pilot_landing_pack(tmp_path, date(2026, 5, 28))

    response = client.get(
        "/integration/operations/reconciliation",
        params={"business_date": "2026-05-28", "landing_root_path": str(tmp_path)},
    )
    assert response.status_code == 200

    payload = response.json()
    assert payload["status"] == "ready"
    assert payload["blocked_count"] == 0
