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
        def publish_clean_inventory(manifests: list[dict[str, object]]) -> list[dict[str, object]]:
            return [{**manifest, "publish_status": "published"} for manifest in manifests]

        publish_clean_inventory(run_dq(validate_schema(create_manifests())))

    wms_inventory_ingestion_dag()
