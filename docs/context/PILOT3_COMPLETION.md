# PILOT-3 Completion Context

Date: 2026-05-29  
Sprint: PILOT-3 Controlled Export Pilot  
Status: completed foundation

## What Was Completed

- Added `PILOT_CONTROLLED_EXPORT_SPEC.md`.
- Extended `apps/backend/open_fnr_api/publication.py` with:
  - `GET /publication/controlled-export/gate`;
  - `GET /publication/controlled-export/reconciliation`;
  - `GET /publication/controlled-export/stop-switch`.
- Controlled export gate now captures:
  - signed pilot scope;
  - ERP and auto-order target restriction;
  - stop switch state;
  - idempotency policy;
  - reconciliation requirement;
  - accountable owner role.
- Added tests for controlled export gate, reconciliation, stop switch and helper eligibility.

## Verification

- Focused regression: `pytest --basetemp tmp\pytest-basetemp tests/backend/test_publication.py tests/backend/test_integration_operations.py tests/backend/test_release_gate.py tests/operations/test_rollback_dr_runbook.py tests/quality/test_text_encoding.py tests/quality/test_no_hardcoded_network_config.py tests/quality/test_no_committed_secrets.py` -> 34 passed, 1 warning about `.pytest_cache` permissions.
- Full regression: `$env:PYTHONPATH='apps/backend;.'; pytest --basetemp tmp\pytest-basetemp` -> 592 passed, 1 warning about `.pytest_cache` permissions.
