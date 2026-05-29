# OPEN FNR Integration And Data Quality UI Specification

Status: UI-3 foundation  
Date: 2026-05-29  
Related sprint: UI-3 Integration And Data Quality UI

## 1. Purpose

This document fixes the UI-3 scope for operational screens used by data operators and data owners to manage source readiness, DQ blockers, retry/reprocess actions and reconciliation before downstream forecasting and replenishment run.

## 2. Functional Scope

| Area | UI capability | Backend contract | Process/audit expectation |
| --- | --- | --- | --- |
| Source readiness | Integration Operations Console shows status, blockers, warnings, owner and recovery action per source contract | `/integration/operations/source-readiness` | Blocked source contracts must create or link recovery tasks. |
| Retry plan | Retry table shows idempotency key, strategy, max attempts, owner and next action | `/integration/operations/retry-plan` | Retry must reuse the same idempotency key and avoid duplicate clean rows. |
| Reconciliation | Reconciliation table shows keys, status, downstream blockers and owner | `/integration/operations/reconciliation` | Forecast, replenishment and publication remain blocked until critical reconciliation blockers are resolved. |
| DQ incident handling | DQ Console shows blocking incidents, affected rows, owner and waiver/rerun actions | `/data-quality/incidents`, `/data-quality/source-contract-runs` | Waivers require authorized role and audit trail. |
| Shadow load gate | Shadow Load Gate shows discovered/missing source files and recovery tasks | `/data/ingestion/pilot-shadow-load/plan` | Missing or invalid source batches open recovery workflow. |

## 3. UI Requirements

- The console must be available from the data workspace route.
- All API calls must use `apiUrl(...)` and central frontend configuration.
- Source readiness, retry plan and reconciliation must be visible on one screen so the operator sees root cause, recovery action and downstream impact together.
- Recovery actions must make idempotency and audit expectations visible before the action is executed.
- DQ blockers must clearly distinguish blocking incidents from warnings.
- UI must not contain hardcoded IP addresses, hostnames, service URLs or port numbers.

## 4. Business Process Coverage

| Process | Steps visible in UI | Acceptance evidence |
| --- | --- | --- |
| Source blocker recovery | Detect blocked contract, assign owner, request resend, rerun DQ, verify reconciliation. | Readiness table, retry table and reconciliation table. |
| DQ waiver | Review incident, confirm owner role, enter reason, approve waiver or rerun check. | DQ incident panel and waiver/rerun action area. |
| Reconciliation control | Compare source contract keys and downstream blockers before publication. | Reconciliation table with keys and blocked downstream consumers. |
| Daily pipeline gate | Validate shadow-load, source DQ, clean publication and feature build stages. | Daily pipeline stage table with process and task columns. |

## 5. Test Requirements

| Test class | Required checks |
| --- | --- |
| UI smoke | Integration Operations Console, Shadow Load Gate, DQ Console and Daily Pipeline Gate are present. |
| API wiring | UI calls source-readiness, retry-plan and reconciliation endpoints through `apiUrl(...)`. |
| Process audit | UI exposes owner, idempotency key, recovery action, downstream blocker and audit expectation. |
| Data validation | DQ blockers, warnings, affected rows and waiver/rerun actions are visible. |
| Accessibility smoke | Integration and DQ sections have accessible labels. |
| Quality gate | No frontend hardcoded network configuration. |

## 6. Acceptance Criteria

UI-3 foundation is accepted when:

- data operators can inspect source readiness, retry plan and reconciliation without database access;
- DQ blockers and waivers are visible in UI context;
- every recovery flow shows owner, action, idempotency and audit requirements;
- automated frontend coverage and frontend build pass.
