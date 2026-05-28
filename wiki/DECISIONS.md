# Architecture Decisions

This page summarizes accepted decisions. Detailed rationale remains in canonical documents.

## ADR-001. License Policy

Decision: use only free self-hosted open-source tools with permissive licenses compatible with Apache License 2.0.

Allowed by default:

- Apache-2.0;
- MIT;
- BSD;
- PostgreSQL License.

Excluded without legal review:

- GPL;
- AGPL;
- SSPL;
- BUSL;
- proprietary SaaS or mandatory proprietary runtime.

References:

- [Project Charter](../PROJECT_CHARTER.md)
- [Technology Architecture](../TECHNOLOGY_ARCHITECTURE.md)

## ADR-002. Production Hardware

Decision: production sizing targets AMD EPYC servers, not legacy LGA 2011-3 / Xeon E5.

Reference:

- [Technology Architecture](../TECHNOLOGY_ARCHITECTURE.md)

## ADR-003. Process Engine

Decision: create a separate subproject named `OPEN FNR Process Engine`.

Engine:

- Flowable OSS;
- BPMN 2.0;
- DMN;
- CMMN;
- PostgreSQL process DB.

Reference:

- [Project Charter](../PROJECT_CHARTER.md)
- [Process Engine Governance](../PROCESS_ENGINE_GOVERNANCE.md)

## ADR-004. Forecast Is Not Order

Decision: separate `forecast`, `demand_projection` and `order_proposal`.

Reference:

- [Technical Specification](../TECHNICAL_SPEC.md)

## ADR-005. Active Matrix Only

Decision: do not calculate a full daily Cartesian product as a monolith. Use active matrix, partitioning and sharding.

Reference:

- [Technology Architecture](../TECHNOLOGY_ARCHITECTURE.md)

## ADR-006. Dev Infrastructure

Decision: use Docker Compose compatible dev infrastructure, without requiring Docker Desktop as a mandatory dependency.

Reference:

- [Dev Infrastructure](../infra/dev/README.md)

## ADR-007. Raw Functional Benchmark Coverage

Decision: functionality from `raw/RELEX Modules and functionality RU.csv` is tracked through a dedicated coverage matrix.

Added scope includes:

- integrated supply chain;
- procurement optimization;
- shelf space optimization;
- capacity optimization;
- supply chain diagnostics;
- promo evaluation;
- supplier collaboration;
- true inventory;
- store management;
- workload forecasting.

Reference:

- [Functional Coverage Matrix](../FUNCTIONAL_COVERAGE_MATRIX.md)
