# OPEN FNR Wiki Home

OPEN FNR is a self-hosted Apache-2.0-compatible platform for demand forecasting and replenishment at large retail scale.

It covers:

- regular demand forecasting;
- promo uplift forecasting;
- demand projection;
- projected stock;
- order proposals;
- replenishment workflows;
- promo workflows;
- fresh and shelf-life;
- multi-echelon planning;
- business process execution through Flowable;
- UI workbenches for planners;
- data, ML, process and security governance.

## Fixed Decisions

| Area | Decision |
| --- | --- |
| License policy | free self-hosted permissive open-source only |
| Target license for project code | Apache License 2.0 |
| Production hardware | AMD EPYC cluster |
| Process engine | Flowable OSS |
| Process notation | BPMN 2.0 |
| Rules | DMN |
| Case management | CMMN |
| Batch orchestration | Apache Airflow |
| Compute | Apache Spark + Polars |
| Forecast/replenishment store | ClickHouse |
| Metadata/process DB | PostgreSQL |
| UI | React + Apache ECharts |
| BI | Apache Superset |

## Current Development Focus

The project is moving from strategic documentation into implementation planning and Sprint 0 bootstrap.

Primary entry point:

- [Project Execution Plan](../PROJECT_EXECUTION_PLAN.md)
- [Development Sprint Plan](../DEVELOPMENT_SPRINT_PLAN.md)

## Local Dev

Local infrastructure is available through:

- [Dev Infrastructure](../infra/dev/README.md)
