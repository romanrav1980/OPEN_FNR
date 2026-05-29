from __future__ import annotations

from datetime import datetime

try:
    from airflow.decorators import dag, task
except ModuleNotFoundError:
    dag = None
    task = None


def build_mdm_manifest(contract_name: str, business_date: str) -> dict[str, object]:
    return {
        "batch_id": f"{contract_name.replace('_', '-')}-{business_date}-v1",
        "source_system": "MDM",
        "contract_name": contract_name,
        "contract_version": "v1",
        "business_date": business_date,
        "idempotency_key": f"MDM:{contract_name}:v1:{business_date}",
    }


def build_mdm_quality_plan(business_date: str) -> dict[str, object]:
    contracts = (
        {
            "contract_name": "mdm_product_line",
            "quality_checks": ("hierarchy_integrity", "lifecycle_validity", "fresh_attributes", "supplier_reference"),
            "blocks": ("assortment", "fresh", "lifecycle", "forecast", "replenishment"),
            "owner_role": "MDM Data Owner",
        },
        {
            "contract_name": "mdm_store_line",
            "quality_checks": ("region_integrity", "timezone_validity", "warehouse_routing", "replenishment_calendar"),
            "blocks": ("store_scope", "replenishment_calendar", "routing", "forecast", "replenishment"),
            "owner_role": "MDM Data Owner",
        },
    )
    return {
        "business_date": business_date,
        "source_system": "MDM",
        "contracts": contracts,
        "required_count": len(contracts),
        "failure_action": "create_mdm_data_owner_recovery_task",
    }


if dag is not None and task is not None:

    @dag(
        dag_id="open_fnr_mdm_reference_ingestion",
        start_date=datetime(2026, 5, 1),
        schedule="@daily",
        catchup=False,
        tags=["open-fnr", "mdm", "reference"],
    )
    def mdm_reference_ingestion_dag():
        @task
        def create_manifests(ds: str) -> list[dict[str, object]]:
            return [
                build_mdm_manifest("mdm_product_line", ds),
                build_mdm_manifest("mdm_store_line", ds),
            ]

        @task
        def validate_schema(manifests: list[dict[str, object]]) -> list[dict[str, object]]:
            return [{**manifest, "schema_status": "validated"} for manifest in manifests]

        @task
        def run_master_data_dq(manifests: list[dict[str, object]]) -> list[dict[str, object]]:
            return [{**manifest, "dq_status": "accepted"} for manifest in manifests]

        @task
        def validate_master_data_quality(manifests: list[dict[str, object]]) -> list[dict[str, object]]:
            plan = build_mdm_quality_plan(str(manifests[0]["business_date"]))
            return [{**manifest, "quality_plan": plan, "quality_status": "accepted"} for manifest in manifests]

        @task
        def publish_reference_data(manifests: list[dict[str, object]]) -> list[dict[str, object]]:
            return [{**manifest, "publish_status": "published"} for manifest in manifests]

        publish_reference_data(validate_master_data_quality(run_master_data_dq(validate_schema(create_manifests()))))

    mdm_reference_ingestion_dag()
