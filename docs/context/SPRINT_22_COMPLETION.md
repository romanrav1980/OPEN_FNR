# Sprint 22 Completion Context

Date: 2026-05-28

## Sprint

Sprint 22: Security And RBAC Hardening.

## Completed Scope

- Added Admin Console backend slice for users, service accounts, access requests and access checks.
- Added RBAC guards for Admin, Security Owner, User Manager and Viewer.
- Added object-level access by region and category.
- Added access request transitions: approve, reject, provision and revoke.
- Added audit event generation for access changes.

## Backend Artifacts

- `apps/backend/open_fnr_api/security.py`
- `tests/backend/test_security.py`
- `apps/backend/open_fnr_api/main.py`
- `tests/backend/test_process_engine.py`

## Process Engine Artifacts

- BPMN: `processes/security/access_request_process.bpmn20.xml`
- DMN: `processes/security/role_assignment_decision.dmn.xml`
- CMMN: `processes/security/security_incident_case.cmmn.xml`
- Registered definitions in `apps/backend/open_fnr_api/process_engine.py`.

## Strengthened Business Process Testing

- BPMN test checks access request classification, review, approve/reject gateway, provisioning, rejection and audit write paths.
- DMN test checks approver/risk outputs and high/medium/low risk rule IDs.
- CMMN test checks incident lifecycle: triage, audit review, revoke suspicious access and closure.
- API tests cover RBAC, denied states, object-level region/category scope, service account visibility and audit trail.

## UI Artifacts

- `apps/frontend/src/main.tsx`
- Admin Console V1 section with users, roles, access requests, audit viewer, denied state and scope explanation.

## Test Report

- HTML report: `docs/test-reports/sprint-22-security-rbac/index.html`
- Screenshot: `docs/test-reports/sprint-22-security-rbac/screenshots/admin-console.png`

## Verification

- `python -m pytest` -> 181 passed.
- `npm.cmd run build` in `apps/frontend` -> completed.
- Playwright screenshot captured.

## Remaining Plan

- Completed: 23 of 37 sprint checkpoints.
- Remaining: 14 sprint checkpoints.
- Approximate remaining time share: 38%.

## Next Sprint

Sprint 23: Stage Rehearsal.
