from fastapi.testclient import TestClient

from open_fnr_api import config
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


def test_promo_manifest_exposes_plan_source() -> None:
    response = client.get("/data/ingestion/manifests/promo-plan")
    assert response.status_code == 200

    manifest = response.json()
    assert manifest["source_system"] == "PROMO"
    assert manifest["contract_name"] == "promo_plan_line"
    assert manifest["contract_version"] == "v1"
    assert manifest["idempotency_key"] == "PROMO:promo_plan_line:v1:2026-05-28"


def test_ingestion_readiness_summarizes_all_real_sources() -> None:
    response = client.get("/data/ingestion/readiness")
    assert response.status_code == 200

    payload = response.json()
    assert payload["status"] == "ready_for_shadow_load"
    assert payload["ready_count"] == payload["total"] == 5
    sources = {pipeline["source_system"] for pipeline in payload["pipelines"]}
    assert sources == {"POS", "WMS", "ERP", "MDM", "PROMO"}
    promo = next(pipeline for pipeline in payload["pipelines"] if pipeline["source_system"] == "PROMO")
    assert "overlap_dq" in promo["blocking_gates"]
    assert "display_capacity_dq" in promo["blocking_gates"]


def test_local_source_file_discovery_uses_configured_landing_path(tmp_path) -> None:
    source_dir = tmp_path / "pos" / "pos_sales_line" / "business_date=2026-05-28"
    source_dir.mkdir(parents=True)
    (source_dir / "sales.csv").write_text("receipt_id,line_id\nr1,1\n", encoding="utf-8")

    original_path = config.settings.landing_root_path
    config.settings.landing_root_path = str(tmp_path)
    try:
        response = client.get(
            "/data/source-adapters/local-files/discover",
            params={
                "source_system": "POS",
                "contract_name": "pos_sales_line",
                "business_date": "2026-05-28",
            },
        )
    finally:
        config.settings.landing_root_path = original_path

    assert response.status_code == 200
    payload = response.json()
    assert payload["total"] == 1
    assert payload["items"][0]["file_name"] == "sales.csv"


def test_local_source_file_discovery_returns_manifest_sidecar(tmp_path) -> None:
    source_dir = tmp_path / "pos" / "pos_sales_line" / "business_date=2026-05-28"
    source_dir.mkdir(parents=True)
    (source_dir / "sales.csv").write_text("receipt_id,line_id\nr1,1\n", encoding="utf-8")
    (source_dir / "manifest.json").write_text(
        """
        {
          "source_system": "POS",
          "contract_name": "pos_sales_line",
          "business_date": "2026-05-28",
          "row_count": 1,
          "checksum": "sha256:test",
          "idempotency_key": "POS:pos_sales_line:v1:2026-05-28",
          "files": ["sales.csv"]
        }
        """,
        encoding="utf-8",
    )

    original_path = config.settings.landing_root_path
    config.settings.landing_root_path = str(tmp_path)
    try:
        response = client.get(
            "/data/source-adapters/local-files/discover",
            params={
                "source_system": "POS",
                "contract_name": "pos_sales_line",
                "business_date": "2026-05-28",
            },
        )
    finally:
        config.settings.landing_root_path = original_path

    assert response.status_code == 200
    payload = response.json()
    assert payload["manifest"]["row_count"] == 1
    assert payload["manifest"]["checksum"] == "sha256:test"
