from datetime import date

from fastapi.testclient import TestClient

from open_fnr_api.clean_publication import (
    CleanPublicationRunMode,
    clean_publication_plans_for_date,
    execute_clean_publication_plan,
)
from open_fnr_api.main import app


client = TestClient(app)


def test_clean_publication_plans_cover_core_raw_to_clean_tables() -> None:
    plans = clean_publication_plans_for_date(date(2026, 5, 28))
    clean_tables = {plan.clean_table for plan in plans}

    assert len(plans) == 6
    assert {
        "open_fnr.clean_sales_daily",
        "open_fnr.clean_stock_snapshot_daily",
        "open_fnr.clean_open_orders",
        "open_fnr.clean_in_transit",
        "open_fnr.clean_prices",
        "open_fnr.clean_promo_plans",
    } == clean_tables
    assert all(plan.idempotency_strategy == "delete_by_source_batch_then_insert" for plan in plans)
    assert all("source_batch_id" in plan.delete_sql for plan in plans)


def test_clean_publication_api_lists_plans_for_business_date() -> None:
    response = client.get("/data/clean-publication/plans", params={"business_date": "2026-05-28"})
    assert response.status_code == 200

    payload = response.json()
    assert payload["total"] == 6
    sales = next(item for item in payload["items"] if item["contract_name"] == "pos_sales_line")
    assert sales["source_batch_id"] == "pos-sales-2026-05-28-v1"
    assert "GROUP BY business_date, store_id, sku_id, batch_id" in sales["insert_sql"]


def test_clean_publication_api_returns_single_plan() -> None:
    response = client.get(
        "/data/clean-publication/plans/clean-promo-2026-05-28",
        params={"business_date": "2026-05-28"},
    )
    assert response.status_code == 200

    payload = response.json()
    assert payload["clean_table"] == "open_fnr.clean_promo_plans"
    assert "open_fnr.raw_promo_plans" in payload["insert_sql"]


def test_clean_publication_api_returns_404_for_unknown_plan() -> None:
    response = client.get(
        "/data/clean-publication/plans/missing-plan",
        params={"business_date": "2026-05-28"},
    )
    assert response.status_code == 404


def test_clean_publication_dry_run_validates_without_sql_execution() -> None:
    plan = clean_publication_plans_for_date(date(2026, 5, 28))[0]
    result = execute_clean_publication_plan(plan, CleanPublicationRunMode.DRY_RUN)

    assert result.status == "validated"
    assert result.executed_statements == ()
    assert result.affected_rows == 0


def test_clean_publication_mock_run_returns_delete_and_insert_statements() -> None:
    plan = clean_publication_plans_for_date(date(2026, 5, 28))[0]
    result = execute_clean_publication_plan(plan, CleanPublicationRunMode.MOCK_RUN)

    assert result.status == "mock_executed"
    assert result.executed_statements == (plan.delete_sql, plan.insert_sql)


def test_clean_publication_run_api_supports_dry_run_with_audit() -> None:
    response = client.post(
        "/data/clean-publication/runs",
        json={
            "business_date": "2026-05-28",
            "actor": "data.platform.owner@example.org",
            "actor_role": "Data Platform Owner",
            "mode": "dry_run",
        },
    )
    assert response.status_code == 200

    payload = response.json()
    assert payload["run_id"] == "clean-publication-2026-05-28-dry_run"
    assert payload["status"] == "ready"
    assert payload["plan_count"] == 6
    assert payload["audit_recorded"] is True
    assert all(result["status"] == "validated" for result in payload["results"])


def test_clean_publication_run_api_supports_mock_run() -> None:
    response = client.post(
        "/data/clean-publication/runs",
        json={
            "business_date": "2026-05-28",
            "actor": "data.platform.owner@example.org",
            "mode": "mock_run",
        },
    )
    assert response.status_code == 200

    payload = response.json()
    assert payload["status"] == "completed"
    assert payload["results"][0]["executed_statements"]
