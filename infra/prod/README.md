# OPEN FNR Production Environment

Status: DEP-1 foundation  
Date: 2026-05-29

Production topology is Kubernetes-first for high availability. Docker Compose may be used only for a non-critical pilot rehearsal or disaster-recovery exercise.

## Rules

- `OPEN_FNR_RUNTIME_MODE=prod`.
- `OPEN_FNR_AUTH_ENABLED=true`.
- `OPEN_FNR_AUTH_DEV_BYPASS_ENABLED=false`.
- No production secret value is committed.
- Hostnames, ports and URLs are injected through environment or orchestration config.
- PostgreSQL, ClickHouse, Flowable, Airflow, OpenSearch and Superset endpoints must use central configuration.
