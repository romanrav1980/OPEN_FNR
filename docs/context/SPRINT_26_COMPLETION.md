# Sprint 26 Completion Context

Date: 2026-05-28

## Sprint

Sprint 26: Production ML And Retraining.

## Completed Scope

- Added production ML governance slice for model candidate, shadow run, drift detection and release gate.
- Added model approval, release and rollback actions with RBAC and audit.
- Added model release gate using WAPE, Bias, baseline comparison, drift and shadow WAPE.
- Added UI Model Monitoring V2 section.

## Backend Artifacts

- `apps/backend/open_fnr_api/ml_governance.py`
- `tests/backend/test_ml_governance.py`
- `apps/backend/open_fnr_api/main.py`
- `tests/backend/test_process_engine.py`

## Process Engine Artifacts

- BPMN: `processes/ml-governance/model_release_process.bpmn20.xml`
- DMN: `processes/ml-governance/model_release_gate_decision.dmn.xml`
- CMMN: `processes/ml-governance/model_drift_case.cmmn.xml`
- Registered definitions in `apps/backend/open_fnr_api/process_engine.py`.

## Strengthened Business Process Testing

- BPMN test checks backtesting, drift detection, shadow comparison, release gate, approval, publish release and rollback paths.
- DMN test checks block, approve and rollback rules.
- CMMN test checks drift triage, shadow review, rollback approval and retraining plan confirmation.
- API tests cover WAPE/Bias, baseline comparison, drift smoke, shadow run, release RBAC, rollback and audit.

## UI Artifacts

- `apps/frontend/src/main.tsx`
- Model Monitoring V2 section with candidate metrics, release steps and action panel.

## Test Report

- HTML report: `docs/test-reports/sprint-26-production-ml-retraining/index.html`
- Screenshot: `docs/test-reports/sprint-26-production-ml-retraining/screenshots/model-monitoring-v2.png`

## Verification

- `python -m pytest` -> 212 passed.
- `npm.cmd run build` in `apps/frontend` -> completed.
- Playwright screenshot captured.

## Remaining Plan

- Completed: 27 of 37 sprint checkpoints.
- Remaining: 10 sprint checkpoints.
- Approximate remaining time share: 27%.

## Next Sprint

Sprint 27: Production Replenishment Scale.
