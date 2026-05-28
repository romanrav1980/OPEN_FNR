# Sprint 28 Completion Context

Date: 2026-05-28

## Sprint

Sprint 28: Production Process Governance.

## Completed Scope

- Added process version list and deployment/change request model.
- Added process change deployment guarded by Release Manager.
- Added process rollback guarded by Release Manager or Process Owner.
- Added migration safety and release notes fields.
- Added UI Process Governance section.

## Backend Artifacts

- `apps/backend/open_fnr_api/process_governance.py`
- `tests/backend/test_process_governance.py`
- `apps/backend/open_fnr_api/main.py`
- `tests/backend/test_process_engine.py`

## Process Engine Artifacts

- BPMN: `processes/process-governance/process_change_management_process.bpmn20.xml`
- DMN: `processes/process-governance/process_change_risk_decision.dmn.xml`
- CMMN: `processes/process-governance/process_incident_case.cmmn.xml`
- Registered definitions in `apps/backend/open_fnr_api/process_engine.py`.

## Strengthened Business Process Testing

- BPMN test checks artifact validation, process test suite, risk decision, approval, rejection, deployment, migration and release notes.
- DMN test checks risk routing by tests, existing instances and artifact kind.
- CMMN test checks deployment incident triage, migration review, rollback approval and process recovery.
- API tests cover version listing, change requests, deployment RBAC, rollback and deployability rules.

## UI Artifacts

- `apps/frontend/src/main.tsx`
- Process Governance section with versions, deployment history, migration status and rollback action.

## Test Report

- HTML report: `docs/test-reports/sprint-28-process-governance/index.html`
- Screenshot: `docs/test-reports/sprint-28-process-governance/screenshots/process-governance.png`

## Verification

- `python -m pytest` -> 228 passed.
- `npm.cmd run build` in `apps/frontend` -> completed.
- Playwright screenshot captured.

## Remaining Plan

- Completed: 29 of 37 sprint checkpoints.
- Remaining: 8 sprint checkpoints.
- Approximate remaining time share: 22%.

## Next Sprint

Sprint 29: Observability And Support.
