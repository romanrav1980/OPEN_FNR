# OPEN FNR Reload Checkpoint - 2026-05-29 PN-2

Use this checkpoint after session restart.

## Latest Pushed Commit

`9380fb7` - `Fix PN-2 remaining sprint count`

## Current Project Focus

Continue executing the fixed sprint plan until completion:

- Supplement 1 implementation: `SUP-1...SUP-10`.
- Process Navigator implementation: `PN-2...PN-6`.
- Real integrations, production security, UI productization, load gate and pilot remain in `NEXT_DELIVERY_PLAN.md`.

## Completed In Latest Block

- `PN-1 Process Navigator Backend Map Contract` completed.
- `PN-2 Process Navigator UI Shell` completed.
- Process Navigator technical specification: `PROCESS_NAVIGATOR_MAP_SPEC.md`.
- Supplement 1 sprint plan: `SUPPLEMENT_1_IMPLEMENTATION_SPRINT_PLAN.md`.
- Tactical delivery plan updated: `NEXT_DELIVERY_PLAN.md`.

## Process Navigator Implementation

Backend:

- `apps/backend/open_fnr_api/process_navigator.py`
- `/process-navigator/map?zoom=0..4`
- `/process-navigator/alerts`
- `/process-navigator/processes/{process_key}/drilldown`
- tests: `tests/backend/test_process_navigator.py`

Frontend:

- route: `#/process-navigator`
- files:
  - `apps/frontend/src/main.tsx`
  - `apps/frontend/src/styles.css`
- UI has semantic zoom controls, process map nodes, selected BPMN detail panel, alert table and edge list.

Evidence:

- `docs/test-reports/sprint-process-navigator-map/index.html`
- `docs/test-reports/sprint-pn-2-process-navigator-ui/index.html`
- screenshot: `docs/test-reports/sprint-pn-2-process-navigator-ui/screenshots/process-navigator-map.png`

## Latest Verification

- `pytest tests/backend/test_process_navigator.py tests/quality/test_text_encoding.py tests/quality/test_no_hardcoded_network_config.py` -> `8 passed`
- `npm.cmd run build` in `apps/frontend` -> passed

## MCP Setup

Docker MCP Toolkit was configured locally, not committed:

- enabled servers: `clickhouse`, `docker`, `filesystem`, `git`, `memory`, `playwright`
- project `.mcp.json` is local/untracked and includes `MCP_DOCKER`, filesystem, memory, postgres and sqlite
- after restart, MCP tools may require the client to reload MCP configuration

Do not commit local `.claude/`, `.mcp.json` or `CLAUDE.md` unless explicitly requested.

## Next Recommended Sprint

Start `SUP-1 Source SLA Runtime Controls`.

Required outcome:

- source SLA runtime model for POS/WMS/ERP/MDM/promo;
- degraded mode and publish block/waiver decision;
- Process Engine tasks for source owners;
- UI surface for SLA matrix and breach handling;
- backend/process/data/security tests;
- HTML evidence report with screenshots if UI is touched.

## Remaining Sprint Count

After PN-2: approximately `26` sprints remain until controlled pilot.
