# OPEN FNR UI Productization Plan

Date: 2026-05-28

## Goal

Convert the current demo control tower into a production UI with routing, feature modules, real API calls, forms, validation, error states and E2E tests.

## Current State

The current UI is a single React page that demonstrates all implemented modules and produces screenshot evidence for sprint reports.

This is useful for validation, but not sufficient for production users.

## Target UI Structure

| Route | Primary users | Purpose |
| --- | --- | --- |
| `/dashboard` | Business Owner, Viewer | Operational overview |
| `/data-loads` | Data Engineer, Data Owner | Ingestion and DQ status |
| `/forecast` | Forecast Planner | Regular forecast review and adjustments |
| `/promo` | Promo Planner, Category Manager | Promo planning and promo uplift |
| `/replenishment` | Replenishment Planner | Projected stock and order proposals |
| `/exceptions` | All planners | Exception center |
| `/process/tasks` | All process roles | Flowable task inbox |
| `/procurement` | Supply Chain Manager | Supplier selection and purchase proposals |
| `/shelf-space` | Category Manager, Store Operations | Planogram and display capacity |
| `/capacity` | Supply Chain Manager | Capacity smoothing and workload |
| `/diagnostics` | Supply Chain Manager | Root cause diagnostics |
| `/suppliers` | Supplier User, Internal Coordinator | Supplier collaboration |
| `/stores` | Store Operations | Store tasks and true inventory |
| `/admin/security` | Admin, Auditor | Users, roles, scopes and audit |

## Technical Plan

| Step | Output |
| --- | --- |
| 1 | Add React Router |
| 2 | Split current `main.tsx` into feature page components |
| 3 | Add API client with generated or typed contracts |
| 4 | Add global auth/session state |
| 5 | Add role-aware navigation |
| 6 | Add loading, empty, error and denied states |
| 7 | Replace static arrays with API calls |
| 8 | Add forms for approve, reject, adjust, confirm and export actions |
| 9 | Add ECharts charts where analytical comparison is needed |
| 10 | Add Playwright E2E tests per business process |
| 11 | Add contextual help footnotes for important UI elements with links to specs and process artifacts |

## UX Rules

- Operational screens must be dense, scan-friendly and work-focused.
- Cards are used only for repeated items or compact summaries.
- Tables must support filters, sort and drill-down.
- Every action must show result status and audit reference.
- Error states must explain what failed and what the user can do.
- Object-level access denial must be visible and auditable.
- Every important UI element must expose a help footnote.
- Help footnotes must explain what the element does, why it matters, which business process it supports and where the task/specification is documented.
- Help footnotes must link to the relevant project document and, when applicable, BPMN/DMN/CMMN artifact or Process Engine process key.
- Help content must be accessible by keyboard and screen reader.

## Acceptance Criteria

- Core pilot users can complete their workflows without the demo control tower.
- UI reads real API data.
- UI writes create audit events.
- Routes are protected by role and object scope.
- E2E tests cover forecast, replenishment, promo, supplier and store workflows.
- Visual regression screenshots are produced for release candidates.
- UI screens cannot be accepted without tested help footnotes for important actions, filters, statuses, metrics, charts, tables and form fields.
