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
        def publish_reference_data(manifests: list[dict[str, object]]) -> list[dict[str, object]]:
            return [{**manifest, "publish_status": "published"} for manifest in manifests]

        publish_reference_data(run_master_data_dq(validate_schema(create_manifests())))

    mdm_reference_ingestion_dag()
