from datetime import date

from fastapi.testclient import TestClient

from open_fnr_api import config
from open_fnr_api.main import app
from open_fnr_api.ingestion import PILOT_REQUIRED_SOURCE_CONTRACTS, build_pilot_shadow_load_plan


client = TestClient(app)


def write_source_file_with_manifest(root, source_system: str, contract_name: str, business_date: str = "2026-05-28") -> None:
    source_dir = root / source_system.lower() / contract_name / f"business_date={business_date}"
    source_dir.mkdir(parents=True)
    file_name = f"{contract_name}.csv"
    (source_dir / file_name).write_text("id,value\n1,ok\n", encoding="utf-8")
    (source_dir / "manifest.json").write_text(
        f"""
        {{
          "source_system": "{source_system}",
          "contract_name": "{contract_name}",
          "business_date": "{business_date}",
          "row_count": 1,
          "checksum": "sha256:{source_system.lower()}-{contract_name}-{business_date}",
          "idempotency_key": "{source_system}:{contract_name}:v1:{business_date}",
          "files": ["{file_name}"]
        }}
        """,
        encoding="utf-8",
    )


def test_contracts_endpoint_lists_core_domains() -> None:
    response = client.get("/data/contracts")
    assert response.status_code == 200

    payload = response.json()
    domains = {item["domain"] for item in payload["contracts"]}
    assert {"sales", "stock", "prices", "product_mdm", "store_mdm", "calendar"} <= domains
    sales_contract = next(item for item in payload["contracts"] if item["domain"] == "sales")
    assert sales_contract["model"] == "PosSalesLine"
    assert payload["freeze_status"] == "ri_1_frozen"
    assert payload["source_contract_count"] == len(PILOT_REQUIRED_SOURCE_CONTRACTS)
    source_contract_names = {item["contract_name"] for item in payload["source_contracts"]}
    assert {contract.contract_name for contract in PILOT_REQUIRED_SOURCE_CONTRACTS} == source_contract_names


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


def test_dwh_sales_history_manifest_exposes_training_history_source() -> None:
    response = client.get("/data/ingestion/manifests/dwh-sales-history")
    assert response.status_code == 200

    manifest = response.json()
    assert manifest["source_system"] == "DWH"
    assert manifest["contract_name"] == "dwh_sales_history_line"
    assert manifest["contract_version"] == "v1"
    assert manifest["idempotency_key"] == "DWH:dwh_sales_history_line:v1:2026-05-28"
    assert manifest["checksum"].startswith("sha256:")


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
    assert payload["ready_count"] == payload["total"] == 6
    sources = {pipeline["source_system"] for pipeline in payload["pipelines"]}
    assert sources == {"POS", "DWH", "WMS", "ERP", "MDM", "PROMO"}
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


def test_pilot_shadow_load_plan_blocks_when_required_sources_are_missing(tmp_path) -> None:
    write_source_file_with_manifest(tmp_path, "POS", "pos_sales_line")

    original_path = config.settings.landing_root_path
    config.settings.landing_root_path = str(tmp_path)
    try:
        response = client.get("/data/ingestion/pilot-shadow-load/plan", params={"business_date": "2026-05-28"})
    finally:
        config.settings.landing_root_path = original_path

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "recovery_required"
    assert payload["discovered_count"] == 1
    assert payload["required_count"] == len(PILOT_REQUIRED_SOURCE_CONTRACTS)
    assert payload["next_gate"] == "source_recovery"
    assert any(task["source_system"] == "WMS" for task in payload["recovery_tasks"])


def test_pilot_shadow_load_plan_is_ready_when_all_contracts_have_files_and_manifests(tmp_path) -> None:
    for contract in PILOT_REQUIRED_SOURCE_CONTRACTS:
        write_source_file_with_manifest(tmp_path, contract.source_system, contract.contract_name)

    original_path = config.settings.landing_root_path
    config.settings.landing_root_path = str(tmp_path)
    try:
        response = client.get("/data/ingestion/pilot-shadow-load/plan", params={"business_date": "2026-05-28"})
    finally:
        config.settings.landing_root_path = original_path

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ready_for_clean_publication"
    assert payload["discovered_count"] == payload["required_count"] == len(PILOT_REQUIRED_SOURCE_CONTRACTS)
    assert payload["recovery_tasks"] == []
    promo = next(source for source in payload["sources"] if source["source_system"] == "PROMO")
    assert "promo_forecast" in promo["required_for"]
    assert promo["checksum"].startswith("sha256:promo")


def test_pilot_shadow_load_helper_detects_manifest_mismatch(tmp_path) -> None:
    source_dir = tmp_path / "pos" / "pos_sales_line" / "business_date=2026-05-28"
    source_dir.mkdir(parents=True)
    (source_dir / "actual.csv").write_text("id,value\n1,ok\n", encoding="utf-8")
    (source_dir / "manifest.json").write_text(
        """
        {
          "source_system": "POS",
          "contract_name": "pos_sales_line",
          "business_date": "2026-05-28",
          "row_count": 1,
          "checksum": "sha256:pos-mismatch",
          "idempotency_key": "POS:pos_sales_line:v1:2026-05-28",
          "files": ["missing.csv"]
        }
        """,
        encoding="utf-8",
    )

    original_path = config.settings.landing_root_path
    config.settings.landing_root_path = str(tmp_path)
    try:
        plan = build_pilot_shadow_load_plan(date.fromisoformat("2026-05-28"))
        response = client.get("/data/ingestion/pilot-shadow-load/plan", params={"business_date": "2026-05-28"})
    finally:
        config.settings.landing_root_path = original_path

    assert plan.required_count == len(PILOT_REQUIRED_SOURCE_CONTRACTS)
    pos = next(source for source in response.json()["sources"] if source["source_system"] == "POS")
    assert pos["status"] == "manifest_mismatch"
