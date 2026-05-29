from fastapi.testclient import TestClient

from open_fnr_api import shadow_gate
from open_fnr_api.main import app


client = TestClient(app)


def test_shadow_load_gate_creates_recovery_tasks_for_missing_files(tmp_path) -> None:
    response = client.post(
        "/data/ingestion/shadow-load/run",
        json={
            "business_date": "2026-05-28",
            "actor": "data.engineer@example.org",
            "actor_role": "Data Engineer",
            "landing_root_path": str(tmp_path),
        },
    )
    assert response.status_code == 200

    payload = response.json()
    assert payload["status"] == "recovery_required"
    assert payload["process_instance_id"] == "proc-shadow-load-2026-05-28"
    assert payload["report"]["missing_contracts"] == 11
    assert len(payload["recovery_tasks"]) == 11
    assert {task["case_key"] for task in payload["recovery_tasks"]} == {"source_batch_recovery_case"}
    assert payload["audit_recorded"] is True


def test_shadow_load_gate_is_ready_when_all_files_are_present(tmp_path) -> None:
    contracts = (
        ("pos", "pos_sales_line"),
        ("dwh", "dwh_sales_history_line"),
        ("wms", "wms_stock_snapshot_line"),
        ("wms", "wms_open_order_line"),
        ("wms", "wms_in_transit_line"),
        ("erp", "erp_price_line"),
        ("erp", "erp_order_export_status_line"),
        ("erp", "erp_supplier_term_line"),
        ("mdm", "mdm_product_line"),
        ("mdm", "mdm_store_line"),
        ("promo", "promo_plan_line"),
    )
    for source, contract in contracts:
        source_dir = tmp_path / source / contract / "business_date=2026-05-28"
        source_dir.mkdir(parents=True)
        (source_dir / f"{contract}.json").write_text("{}", encoding="utf-8")

    response = client.post(
        "/data/ingestion/shadow-load/run",
        json={
            "business_date": "2026-05-28",
            "actor": "data.engineer@example.org",
            "landing_root_path": str(tmp_path),
        },
    )
    assert response.status_code == 200

    payload = response.json()
    assert payload["status"] == "ready_for_validation"
    assert payload["report"]["missing_contracts"] == 0
    assert payload["recovery_tasks"] == []


def test_shadow_load_gate_creates_dq_recovery_tasks_when_dq_blocks_after_discovery(tmp_path) -> None:
    contracts = (
        ("pos", "pos_sales_line"),
        ("dwh", "dwh_sales_history_line"),
        ("wms", "wms_stock_snapshot_line"),
        ("wms", "wms_open_order_line"),
        ("wms", "wms_in_transit_line"),
        ("erp", "erp_price_line"),
        ("erp", "erp_order_export_status_line"),
        ("erp", "erp_supplier_term_line"),
        ("mdm", "mdm_product_line"),
        ("mdm", "mdm_store_line"),
        ("promo", "promo_plan_line"),
    )
    for source, contract in contracts:
        source_dir = tmp_path / source / contract / "business_date=2026-05-28"
        source_dir.mkdir(parents=True)
        (source_dir / f"{contract}.json").write_text("", encoding="utf-8")

    response = client.post(
        "/data/ingestion/shadow-load/run",
        json={
            "business_date": "2026-05-28",
            "actor": "data.engineer@example.org",
            "landing_root_path": str(tmp_path),
        },
    )
    assert response.status_code == 200

    payload = response.json()
    assert payload["status"] == "recovery_required"
    assert payload["report"]["missing_contracts"] == 0
    assert len(payload["recovery_tasks"]) == 11
    assert {task["reason"] for task in payload["recovery_tasks"]} == {"dq_blocker"}
    assert payload["recovery_tasks"][0]["available_actions"] == [
        "fix_source",
        "request_resend",
        "approve_waiver",
        "comment",
    ]


def test_recovery_task_owner_routing_is_source_specific() -> None:
    assert shadow_gate.owner_role_for_source("POS") == "Data Engineer"
    assert shadow_gate.owner_role_for_source("DWH") == "Sales Data Owner"
    assert shadow_gate.owner_role_for_source("WMS") == "Supply Chain Data Owner"
    assert shadow_gate.owner_role_for_source("ERP") == "Integration Owner"
    assert shadow_gate.owner_role_for_source("MDM") == "MDM Data Owner"
    assert shadow_gate.owner_role_for_source("PROMO") == "Promo Planner"
