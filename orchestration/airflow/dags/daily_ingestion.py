from __future__ import annotations

from datetime import datetime

from airflow.decorators import dag, task


DOMAINS = ("sales", "stock", "prices", "product_mdm", "store_mdm", "calendar")


@dag(
    dag_id="daily_ingestion",
    schedule="0 2 * * *",
    start_date=datetime(2026, 1, 1),
    catchup=False,
    tags=["open-fnr", "ingestion"],
)
def daily_ingestion() -> None:
    @task
    def register_batch(domain: str) -> dict[str, str]:
        return {
            "domain": domain,
            "status": "waiting",
            "source_system": "mock",
        }

    @task
    def validate_contract(batch: dict[str, str]) -> dict[str, str]:
        return batch | {"contract_status": "accepted"}

    @task
    def publish_status(batch: dict[str, str]) -> dict[str, str]:
        return batch | {"status": "loaded"}

    for domain in DOMAINS:
        publish_status(validate_contract(register_batch(domain)))


daily_ingestion()
