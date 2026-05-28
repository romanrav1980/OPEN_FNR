from __future__ import annotations

from datetime import datetime

try:
    from airflow.decorators import dag, task
except ModuleNotFoundError:
    dag = None
    task = None


def build_pos_sales_manifest(business_date: str) -> dict[str, object]:
    return {
        "batch_id": f"pos-sales-{business_date}-v1",
        "source_system": "POS",
        "contract_name": "pos_sales_line",
        "contract_version": "v1",
        "business_date": business_date,
        "idempotency_key": f"POS:pos_sales_line:v1:{business_date}",
    }


if dag is not None and task is not None:

    @dag(
        dag_id="open_fnr_pos_sales_ingestion",
        start_date=datetime(2026, 5, 1),
        schedule="@daily",
        catchup=False,
        tags=["open-fnr", "pos", "sales"],
    )
    def pos_sales_ingestion_dag():
        @task
        def create_manifest(ds: str) -> dict[str, object]:
            return build_pos_sales_manifest(ds)

        @task
        def validate_schema(manifest: dict[str, object]) -> dict[str, object]:
            return {**manifest, "schema_status": "validated"}

        @task
        def run_dq(manifest: dict[str, object]) -> dict[str, object]:
            return {**manifest, "dq_status": "accepted"}

        @task
        def publish_clean_sales(manifest: dict[str, object]) -> dict[str, object]:
            return {**manifest, "publish_status": "published"}

        publish_clean_sales(run_dq(validate_schema(create_manifest())))

    pos_sales_ingestion_dag()
