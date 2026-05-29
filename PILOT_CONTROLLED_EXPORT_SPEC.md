# OPEN FNR Controlled Export Pilot Specification

Status: PILOT-3 foundation  
Date: 2026-05-29

## 1. Purpose

Controlled export pilot enables limited real publication to ERP and auto-order targets after shadow mode evidence is accepted. The export window must be reversible, idempotent and reconciled before expansion.

## 2. Backend Contract

Controlled export endpoints:

```text
GET /publication/controlled-export/gate
GET /publication/controlled-export/reconciliation
GET /publication/controlled-export/stop-switch
```

The regular publication send/retry endpoints remain the execution boundary:

```text
POST /publication/packages/{package_id}/send
POST /publication/packages/{package_id}/retry
```

## 3. Gate Requirements

| Requirement | Rule |
| --- | --- |
| Scope | Only the signed pilot scope may be exported |
| Targets | ERP and auto-order only for PILOT-3 |
| Stop switch | If active, all controlled exports are blocked |
| Idempotency | Same business key must reuse the same idempotency key and not create duplicate sends |
| Reconciliation | Export cannot be considered complete until source and target statuses are reconciled |
| Owner | Integration Owner owns the gate; Incident Manager owns the stop switch |

## 4. Business Process

1. Business Owner accepts shadow report.
2. Integration Owner opens controlled export window.
3. Publication package is checked for approval, scope and target.
4. Export uses configured target endpoint or mock target in DEV.
5. Reconciliation confirms source and target status.
6. Stop switch remains available during the pilot window.
7. Any failure follows the publication export failure runbook.

## 5. Test Requirements

PILOT-3 tests must verify:

- gate exposes pilot scope, allowed targets and reconciliation requirement;
- stop switch blocks ERP and auto-order targets when active;
- reconciliation proves no duplicate target send;
- controlled export helper rejects non-pilot targets and unapproved package items;
- existing idempotency and retry tests remain green;
- full regression remains green.

## 6. Acceptance Criteria

PILOT-3 is accepted when:

- controlled export gate, reconciliation and stop-switch endpoints are available;
- publication idempotency and retry tests pass;
- controlled export can be stopped before target publication;
- reconciliation evidence is available before export resume or expansion.
