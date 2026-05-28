from fastapi.testclient import TestClient

from open_fnr_api.main import app


client = TestClient(app)


def test_dq_rules_can_filter_by_domain() -> None:
    response = client.get("/data-quality/rules", params={"domain": "sales"})
    assert response.status_code == 200

    payload = response.json()
    assert payload["total"] == 1
    assert payload["items"][0]["rule_id"] == "sales_required_keys"


def test_source_contract_dq_plans_cover_real_ingestion_sources() -> None:
    response = client.get("/data-quality/source-contract-plans")
    assert response.status_code == 200

    payload = response.json()
    assert payload["total"] == 9
    contracts = {item["contract_name"] for item in payload["items"]}
    assert {
        "pos_sales_line",
        "wms_stock_snapshot_line",
        "wms_open_order_line",
        "wms_in_transit_line",
        "erp_price_line",
        "erp_order_export_status_line",
        "mdm_product_line",
        "mdm_store_line",
        "promo_plan_line",
    } == contracts


def test_source_contract_dq_plans_can_filter_by_source_system() -> None:
    response = client.get("/data-quality/source-contract-plans", params={"source_system": "promo"})
    assert response.status_code == 200

    payload = response.json()
    assert payload["total"] == 1
    plan = payload["items"][0]
    assert plan["contract_name"] == "promo_plan_line"
    assert "no_invalid_overlap" in plan["blocking_rules"]
    assert "missing_display_capacity" in plan["warning_rules"]


def test_dq_incidents_can_filter_blocking() -> None:
    response = client.get("/data-quality/incidents", params={"blocking": "true"})
    assert response.status_code == 200

    payload = response.json()
    assert payload["total"] == 1
    assert payload["items"][0]["status"] == "blocking"


def test_dq_waiver_requires_data_owner_or_admin() -> None:
    response = client.post(
        "/data-quality/incidents/dq-20260528-sales-001/waiver",
        json={"reason": "Temporary waiver for test", "approver_role": "Viewer"},
    )
    assert response.status_code == 403


def test_dq_waiver_changes_status_and_blocking_flag() -> None:
    response = client.post(
        "/data-quality/incidents/dq-20260528-sales-001/waiver",
        json={"reason": "Source replay is delayed but forecast can use fallback", "approver_role": "Data Owner"},
    )
    assert response.status_code == 200

    payload = response.json()
    assert payload["status"] == "waived"
    assert payload["blocking"] is False
    assert payload["waiver_reason"] is not None
