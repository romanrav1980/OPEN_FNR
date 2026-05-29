# UI-1 Completion Note

Status: completed foundation  
Date: 2026-05-29  
Sprint: UI-1 Routed Application Foundation

## Scope Completed

- Routed application foundation is accepted based on existing implementation.
- Specification added:
  - `UI_ROUTED_APPLICATION_FOUNDATION_SPEC.md`.
- Verified existing frontend capabilities:
  - hash routes for major workspaces;
  - active route state from browser hash;
  - centralized API/service config through `app_config.ts`;
  - contextual `HelpFootnote` support for UI controls.

## Evidence

- Frontend route/config tests added:
  - `tests/frontend/test_ui_routed_foundation.py`.
- HTML evidence report:
  - `docs/test-reports/sprint-ui-1-routed-foundation/index.html`.
- Targeted tests: 6 passed.
- Frontend build: passed.
- Full regression: 522 passed, 1 local `.pytest_cache` permission warning.

## Deferred

- Full React Router migration.
- Splitting the large control tower file into feature modules.
- Playwright visual/accessibility evidence for productized workflows.

These are deferred to UI-2..UI-5 because UI-1 establishes the route/config/help foundation without destabilizing the existing control tower.
