# PILOT-1 Completion Context

Date: 2026-05-29  
Sprint: PILOT-1 Pilot Scope And Data Readiness  
Status: completed foundation

## What Was Completed

- Added `PILOT_SCOPE_DATA_READINESS_SPEC.md`.
- Extended `apps/backend/open_fnr_api/pilot.py` with:
  - `GET /pilot/scope-signoff`;
  - `GET /pilot/data-readiness`;
  - `GET /pilot/readiness-pack`.
- Pilot scope now includes store count, SKU count and suppliers.
- Readiness pack now includes:
  - signed scope;
  - sales history depth;
  - stock/in-transit readiness;
  - active matrix coverage;
  - promo history depth;
  - pilot business calendar;
  - WAPE, service level, lost sales, overstock and waste thresholds.
- Added tests for scope sign-off, data readiness, history depth and threshold completeness.

## Verification

- Focused regression: `pytest --basetemp tmp\pytest-basetemp tests/backend/test_pilot.py tests/backend/test_ingestion.py tests/backend/test_shadow_gate.py tests/backend/test_pilot_fixtures.py tests/quality/test_text_encoding.py tests/quality/test_no_hardcoded_network_config.py tests/quality/test_no_committed_secrets.py` -> 36 passed, 1 warning about `.pytest_cache` permissions.
- Full regression: `$env:PYTHONPATH='apps/backend;.'; pytest --basetemp tmp\pytest-basetemp` -> 584 passed, 1 warning about `.pytest_cache` permissions.
