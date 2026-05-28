from fastapi.testclient import TestClient

from open_fnr_api.main import app


client = TestClient(app)


def test_contracts_endpoint_lists_core_domains() -> None:
    response = client.get("/data/contracts")
    assert response.status_code == 200

    domains = {item["domain"] for item in response.json()["contracts"]}
    assert {"sales", "stock", "prices", "product_mdm", "store_mdm", "calendar"} <= domains
    sales_contract = next(item for item in response.json()["contracts"] if item["domain"] == "sales")
    assert sales_contract["model"] == "PosSalesLine"


def test_ingestion_status_can_filter_by_domain() -> None:
    response = client.get("/data/ingestion/status", params={"domain": "sales"})
    assert response.status_code == 200

    payload = response.json()
    assert payload["total"] == 1
    assert payload["items"][0]["domain"] == "sales"


def test_ingestion_status_returns_404_for_unknown_batch() -> None:
    response = client.get("/data/ingestion/status/missing-batch")
    assert response.status_code == 404


def test_pos_sales_manifest_exposes_idempotency_checksum_and_landing_uri() -> None:
    response = client.get("/data/ingestion/manifests/pos-sales")
    assert response.status_code == 200

    manifest = response.json()
    assert manifest["source_system"] == "POS"
    assert manifest["contract_name"] == "pos_sales_line"
    assert manifest["contract_version"] == "v1"
    assert manifest["idempotency_key"] == "POS:pos_sales_line:v1:2026-05-28"
    assert manifest["checksum"].startswith("sha256:")
    assert "business_date=2026-05-28" in manifest["landed_uri"]


def test_wms_manifests_expose_projected_stock_inputs() -> None:
    endpoints = {
        "wms-stock": "wms_stock_snapshot_line",
        "wms-open-orders": "wms_open_order_line",
        "wms-in-transit": "wms_in_transit_line",
    }

    for endpoint, contract_name in endpoints.items():
        response = client.get(f"/data/ingestion/manifests/{endpoint}")
        assert response.status_code == 200

        manifest = response.json()
        assert manifest["source_system"] == "WMS"
        assert manifest["contract_name"] == contract_name
        assert manifest["contract_version"] == "v1"
        assert manifest["idempotency_key"] == f"WMS:{contract_name}:v1:2026-05-28"
        assert manifest["checksum"].startswith("sha256:")


def test_erp_manifests_expose_prices_and_order_export_statuses() -> None:
    endpoints = {
        "erp-prices": "erp_price_line",
        "erp-order-statuses": "erp_order_export_status_line",
    }

    for endpoint, contract_name in endpoints.items():
        response = client.get(f"/data/ingestion/manifests/{endpoint}")
        assert response.status_code == 200

        manifest = response.json()
        assert manifest["source_system"] == "ERP"
        assert manifest["contract_name"] == contract_name
        assert manifest["idempotency_key"] == f"ERP:{contract_name}:v1:2026-05-28"


def test_mdm_manifests_expose_product_and_store_reference_sources() -> None:
    endpoints = {
        "mdm-products": "mdm_product_line",
        "mdm-stores": "mdm_store_line",
    }

    for endpoint, contract_name in endpoints.items():
        response = client.get(f"/data/ingestion/manifests/{endpoint}")
        assert response.status_code == 200

        manifest = response.json()
        assert manifest["source_system"] == "MDM"
        assert manifest["contract_name"] == contract_name
        assert manifest["idempotency_key"] == f"MDM:{contract_name}:v1:2026-05-28"
