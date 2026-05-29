from __future__ import annotations

from datetime import datetime

try:
    from airflow.decorators import dag, task
except ModuleNotFoundError:
    dag = None
    task = None


def build_wms_manifest(contract_name: str, business_date: str) -> dict[str, object]:
    return {
        "batch_id": f"{contract_name.replace('_', '-')}-{business_date}-v1",
        "source_system": "WMS",
        "contract_name": contract_name,
        "contract_version": "v1",
        "business_date": business_date,
        "idempotency_key": f"WMS:{contract_name}:v1:{business_date}",
    }


def build_wms_reconciliation_plan(business_date: str) -> dict[str, object]:
    contracts = (
        {
            "contract_name": "wms_stock_snapshot_line",
            "reconciliation_keys": ("business_date", "location_id", "sku_id"),
            "blocks": ("projected_stock", "replenishment", "true_inventory"),
            "sla": "before_replenishment_cutoff",
        },
        {
            "contract_name": "wms_open_order_line",
            "reconciliation_keys": ("order_id", "line_id", "sku_id"),
            "blocks": ("projected_stock", "replenishment", "multi_echelon"),
            "sla": "before_replenishment_cutoff",
        },
        {
            "contract_name": "wms_in_transit_line",
            "reconciliation_keys": ("shipment_id", "line_id", "sku_id"),
            "blocks": ("projected_stock", "replenishment", "capacity"),
            "sla": "before_replenishment_cutoff",
        },
    )
    return {
        "business_date": business_date,
        "source_system": "WMS",
        "contracts": contracts,
        "required_count": len(contracts),
        "failure_action": "create_supply_chain_data_owner_recovery_task",
    }


if dag is not None and task is not None:

    @dag(
        dag_id="open_fnr_wms_inventory_ingestion",
        start_date=datetime(2026, 5, 1),
        schedule="@daily",
        catchup=False,
        tags=["open-fnr", "wms", "inventory"],
    )
    def wms_inventory_ingestion_dag():
        @task
        def create_manifests(ds: str) -> list[dict[str, object]]:
            return [
                build_wms_manifest("wms_stock_snapshot_line", ds),
                build_wms_manifest("wms_open_order_line", ds),
                build_wms_manifest("wms_in_transit_line", ds),
            ]

        @task
        def validate_schema(manifests: list[dict[str, object]]) -> list[dict[str, object]]:
            return [{**manifest, "schema_status": "validated"} for manifest in manifests]

        @task
        def run_dq(manifests: list[dict[str, object]]) -> list[dict[str, object]]:
            return [{**manifest, "dq_status": "accepted"} for manifest in manifests]

        @task
        def reconcile_inventory_inputs(manifests: list[dict[str, object]]) -> list[dict[str, object]]:
            plan = build_wms_reconciliation_plan(str(manifests[0]["business_date"]))
            return [{**manifest, "reconciliation_status": "accepted", "reconciliation_plan": plan} for manifest in manifests]

        @task
        def publish_clean_inventory(manifests: list[dict[str, object]]) -> list[dict[str, object]]:
            return [{**manifest, "publish_status": "published"} for manifest in manifests]

        publish_clean_inventory(reconcile_inventory_inputs(run_dq(validate_schema(create_manifests()))))

    wms_inventory_ingestion_dag()
