# OPEN FNR Rollback And DR Drill Runbook

Status: DEP-4 foundation  
Date: 2026-05-29  
Related sprint: DEP-4 Rollback And DR Drill

## Purpose

This runbook defines the production recovery drill for a failed OPEN FNR release. It extends the backup/restore smoke procedure with application rollback, migration recovery, degraded mode and controlled export recovery.

The drill must prove that a failed release has a documented recovery path before pilot exports are enabled.

## Preconditions

| Area | Required Evidence |
| --- | --- |
| Release candidate | `/release-gate/candidate` has no blocking critical defects |
| Rollback plan | `/release-gate/rollback-plan` returns `ready=true` |
| Backup/restore | Latest backup manifest and restore-smoke evidence are available |
| Observability | Incident runbook and alert rules are available |
| Export control | Publication stop switch can keep ERP/auto-order exports queued |

## Drill Steps

| Step | Action | Why | Expected Result |
| --- | --- | --- | --- |
| 1 | Open a release incident and classify severity. | Establishes SLA, owner and audit trail. | Incident Manager owns the recovery. |
| 2 | Freeze controlled exports. | Prevents duplicate orders and duplicate supplier/publication messages. | ERP and auto-order exports stay queued. |
| 3 | Restore the previous approved application version. | Returns the system to a known compatible application state. | `/health` and `/ready` pass for the previous version. |
| 4 | Execute migration rollback or forward-fix decision. | Protects schema compatibility and avoids partial recovery. | Schema compatibility check passes. |
| 5 | Validate backup/restore smoke evidence. | Proves the data recovery path is viable. | Manifest checksum and restore evidence are attached. |
| 6 | Activate degraded mode if needed. | Keeps business users in safe review mode while exports remain blocked. | Forecast, replenishment and BI are read-only; exports are blocked. |
| 7 | Run reconciliation gate. | Confirms no duplicate or missing publication state. | Reconciliation passes or export resume is rejected. |
| 8 | Resume controlled exports only after approval. | Restores operational flow safely. | Release Manager and Incident Manager approve resume. |
| 9 | Write DR evidence. | Leaves audit evidence for pilot readiness. | Release incident contains RPO/RTO and recovery evidence. |

## Degraded Mode

The default degraded mode is `shadow_review_only`.

| Allowed | Blocked |
| --- | --- |
| Data ingestion review | ERP export |
| Forecast review | Auto-order export |
| Replenishment review | Bulk approval |
| BI read-only | Supplier publication |

## Acceptance Gate

DEP-4 is accepted when:

- rollback and DR drill API endpoints are available;
- BPMN `rollback_drill_process` covers export freeze, application rollback, migration recovery, restore smoke, degraded mode, reconciliation and evidence write;
- tests validate rollback plan, DR evidence, degraded mode and BPMN structure;
- full regression remains green.
