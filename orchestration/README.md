# OPEN FNR Orchestration

Airflow DAG definitions for local and production batch orchestration.

Sprint 1 adds `daily_ingestion`, a skeleton DAG for inbound domain loading:

- sales;
- stock;
- prices;
- product MDM;
- store MDM;
- calendar.

The implementation intentionally starts with explicit task boundaries, because
later sprints will attach real source connectors, DQ gates and process-engine
callbacks.
