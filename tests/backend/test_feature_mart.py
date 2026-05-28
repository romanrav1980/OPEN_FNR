from fastapi.testclient import TestClient

from open_fnr_api.main import app


client = TestClient(app)


def test_active_matrix_summary_returns_totals() -> None:
    response = client.get("/feature-mart/active-matrix")
    assert response.status_code == 200

    payload = response.json()
    assert payload["total"] == 2
    assert payload["active_pairs_total"] == 2140000


def test_feature_definitions_are_point_in_time_safe() -> None:
    response = client.get("/feature-mart/features")
    assert response.status_code == 200

    payload = response.json()
    assert payload["point_in_time_safe"] is True
    assert {item["feature_group"] for item in payload["items"]} >= {"lag", "rolling", "price", "stock"}


def test_feature_version_detail() -> None:
    response = client.get("/feature-mart/versions/fm-20260528-001")
    assert response.status_code == 200
    assert response.json()["status"] == "published"


def test_feature_version_unknown_returns_404() -> None:
    response = client.get("/feature-mart/versions/missing")
    assert response.status_code == 404


def test_feature_build_plan_links_clean_dependencies_to_feature_store() -> None:
    response = client.get("/feature-mart/build-plans", params={"business_date": "2026-05-28"})
    assert response.status_code == 200

    payload = response.json()
    assert payload["total"] == 1
    plan = payload["items"][0]
    assert plan["feature_version"] == "fm-20260528-001"
    assert plan["dependency_count"] == 6
    assert plan["output_table"] == "open_fnr.feature_store_daily"
    assert "no_future_fact_leakage" in plan["validation_rules"]
    assert {item["source_table"] for item in plan["dependencies"]} >= {
        "open_fnr.clean_sales_daily",
        "open_fnr.clean_stock_snapshot_daily",
        "open_fnr.clean_prices",
        "open_fnr.clean_promo_plans",
    }


def test_feature_build_plan_detail_returns_404_for_unknown_plan() -> None:
    response = client.get(
        "/feature-mart/build-plans/missing",
        params={"business_date": "2026-05-28"},
    )
    assert response.status_code == 404


def test_feature_build_run_dry_run_validates_and_records_audit() -> None:
    response = client.post(
        "/feature-mart/build-runs",
        json={
            "business_date": "2026-05-28",
            "actor": "data.science.owner@example.org",
            "actor_role": "Data Science Owner",
            "mode": "dry_run",
        },
    )
    assert response.status_code == 200

    payload = response.json()
    assert payload["status"] == "validated"
    assert payload["validation_status"] == "accepted"
    assert payload["dependency_count"] == 6
    assert payload["audit_recorded"] is True


def test_feature_build_run_mock_publishes_feature_version() -> None:
    response = client.post(
        "/feature-mart/build-runs",
        json={
            "business_date": "2026-05-28",
            "actor": "data.science.owner@example.org",
            "mode": "mock_run",
        },
    )
    assert response.status_code == 200
    assert response.json()["status"] == "published"
