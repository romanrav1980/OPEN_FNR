# OPEN FNR UI E2E Visual Accessibility Suite Specification

Status: UI-5 foundation  
Date: 2026-05-29  
Related sprint: UI-5 UI E2E Visual Accessibility Suite

## 1. Purpose

This document fixes the UI-5 pilot safety net for routed UI workflows. The current foundation uses static and build-time gates that do not require adding new browser dependencies. A later deployment-hardening pass may replace or extend this with a full Playwright browser runner when the target environment provides managed browser binaries.

## 2. Covered Routes And Workflows

| Route/workspace | Workflow coverage |
| --- | --- |
| `#/control-tower` | Executive status, process map, service links and high-level operations. |
| `#/data` | Shadow load, DQ, integration operations, daily pipeline and feature mart. |
| `#/forecast` | Forecast workbench, promo workbench and promo uplift forecast. |
| `#/replenishment` | Inventory projection, order proposal, replenishment workbench, exceptions and adjustments. |
| `#/operations` | Publication, KPI, fresh, lifecycle, multi-echelon, supplier and capacity operations. |
| `#/admin` | Security, admin, service accounts, access review and process deployment governance. |
| `#/process-navigator` | Process map, zoom, alerts, conformance, performance, versions and infrastructure linkage. |

## 3. Test Layers

| Layer | Foundation implementation | Future browser extension |
| --- | --- | --- |
| Smoke | Static tests verify required sections and route markers. | Navigate each route and assert visible headings. |
| Validation | Static tests verify blocker, waiver, denied, retry, audit and process text. | Submit form states and validate errors. |
| RBAC/security | Static tests verify denied state, service account and object-scope context. | Execute role-based scenarios against mocked auth claims. |
| Visual | HTML evidence reports summarize each workflow and link sprint artifacts. | Capture desktop/tablet/mobile screenshots for each route. |
| Accessibility | Static tests verify aria labels, button types and keyboard/process-navigator requirements. | Run automated WCAG checks and keyboard navigation scripts. |
| Network config | Quality gate rejects hardcoded service URLs, hosts, ports and IP addresses in source. | Same gate runs before browser tests. |

## 4. Acceptance Criteria

UI-5 foundation is accepted when:

- all UI-1..UI-4 frontend tests pass together;
- the frontend production build passes;
- full backend/frontend regression passes;
- HTML evidence reports exist for UI-1..UI-5;
- the focused sprint plan marks R4 UI productization as completed foundation;
- remaining project plan moves to ML/replenishment production.

## 5. Deferred Browser Runner Criteria

The full browser runner is intentionally deferred until deployment hardening when browser dependencies can be governed with the same repository policy as the rest of the stack. The runner must use only Apache-2.0-compatible tooling and central configuration for any host, port or base URL.
