# OPEN FNR Supplement 1 Adoption Matrix

Date: 2026-05-29
Status: adopted into project governance, API gates and regression tests.

## Scope

[TECHNICAL_SPEC_SUPPLEMENT_1.md](TECHNICAL_SPEC_SUPPLEMENT_1.md) is accepted as a mandatory supplement to the project charter and technical specification. It has priority for operational requirements, governance and production acceptance.

## Section Coverage

| Supplement section | Project decision | Implemented control |
| --- | --- | --- |
| A. Source Data SLA | Mandatory before production; failed SLA opens incident and blocks publication by default | `/supplement/source-sla`, `/supplement/source-sla/evaluate` |
| B. ML Lifecycle | EXPERIMENT -> CANDIDATE -> SHADOW -> CHAMPION/CHALLENGER -> RETIRED; 26-week backtest; 14-day shadow | `/supplement/ml-lifecycle` |
| C. Replenishment Finance | Holding cost, lost sales, waste and service levels require business sign-off | `/supplement/replenishment-financial-parameters` |
| D. Parallel Run And Acceptance | Shadow, Parallel Run and Controlled Pilot have evidence and sign-off gates | `/supplement/business-acceptance` |
| E. DR/BC | RPO/RTO and backup policy remain in strategic documentation and support runbooks | `BUSINESS_CONTINUITY_DR.md` if/when created; current gate in this matrix |
| F. Lineage And Ownership | Lineage, ownership domains and retention policy are mandatory | `/supplement/data-governance` |
| G. API Versioning | Public APIs use `/api/v{major}/`, 90-day deprecation and registries | `/supplement/api-governance` |
| H. Data Classification And Supplier Isolation | C1-C4 classification, supplier `supplier_id` isolation and audit | `/supplement/supplier-isolation` |
| I. Intraday Scope | Intraday/demand sensing is out of v1; fresh gets compensating controls | `/supplement/scope/intraday` |
| J. Historical Simulation | >= 52-week replenishment simulation is required before Parallel Run | `/supplement/historical-simulation` |
| K. Notifications And Escalation | Notification channels and human task SLA are mandatory | `/supplement/notifications`, `/supplement/human-task-sla` |
| L. OTB Scope | OTB/budget-aware replenishment is out of v1 and planned for v2 | `/supplement/scope/otb` |
| M. Open Questions | M-01...M-12 are tracked as business blockers | `/supplement/open-questions` |

## Documents Updated By This Adoption

| Document | Supplement impact |
| --- | --- |
| `TECHNICAL_SPEC.md` | Supplement is treated as an addendum and production governance source |
| `PROJECT_CHARTER.md` | Project charter accepts Supplement 1 as mandatory operational baseline |
| `DATA_GOVERNANCE.md` | Source SLA, lineage, retention and ownership are reinforced |
| `ML_GOVERNANCE.md` | Lifecycle, shadow, fallback and emergency rollback are reinforced |
| `REAL_DATA_INGESTION_PIPELINES.md` | Source SLA and degraded publication behavior are now explicit gates |
| `PILOT_LAUNCH_PLAN.md` | Historical Simulation, Shadow Mode and Parallel Run become mandatory gates |
| `INTEGRATION_STRATEGY.md` | API versioning, deprecation, consumer registry and ITSM webhook are explicit |
| `SECURITY_STRATEGY.md` | Supplier isolation and C1-C4 classification are explicit |
| `TESTING_STRATEGY.md` | Supplement gates are included in backend regression |

## Test Coverage

Backend regression includes:

- `tests/backend/test_supplement_governance.py`
- `tests/quality/test_text_encoding.py`
- `tests/quality/test_no_hardcoded_network_config.py`

## Open External Inputs

The following decisions remain business or IT inputs and cannot be invented by engineering:

- Signed Data SLA Agreements with each source owner.
- Service level targets by segment/category.
- Holding cost and lost sales parameters.
- Matched-pairs control group.
- Real enterprise IdP values.
- ITSM target and credentials.
- OTB source system for v2.
