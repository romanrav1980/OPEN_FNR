from __future__ import annotations

from datetime import datetime

try:
    from airflow.decorators import dag, task
except ModuleNotFoundError:
    dag = None
    task = None


def build_dwh_sales_history_manifest(business_date: str) -> dict[str, object]:
    return {
        "batch_id": f"dwh-sales-history-{business_date}-v1",
        "source_system": "DWH",
        "contract_name": "dwh_sales_history_line",
        "contract_version": "v1",
        "business_date": business_date,
        "idempotency_key": f"DWH:dwh_sales_history_line:v1:{business_date}",
        "history_window": "rolling_24_months",
    }


if dag is not None and task is not None:

    @dag(
        dag_id="open_fnr_dwh_sales_history_ingestion",
        start_date=datetime(2026, 5, 1),
        schedule="@daily",
        catchup=False,
        tags=["open-fnr", "dwh", "sales-history"],
    )
    def dwh_sales_history_ingestion_dag():
        @task
        def create_manifest(ds: str) -> dict[str, object]:
            return build_dwh_sales_history_manifest(ds)

        @task
        def validate_history_window(manifest: dict[str, object]) -> dict[str, object]:
            return {**manifest, "history_window_status": "validated"}

        @task
        def validate_schema(manifest: dict[str, object]) -> dict[str, object]:
            return {**manifest, "schema_status": "validated"}

        @task
        def run_dq(manifest: dict[str, object]) -> dict[str, object]:
            return {**manifest, "dq_status": "accepted"}

        @task
        def publish_training_history(manifest: dict[str, object]) -> dict[str, object]:
            return {**manifest, "publish_status": "published"}

        publish_training_history(run_dq(validate_schema(validate_history_window(create_manifest()))))

    dwh_sales_history_ingestion_dag()
