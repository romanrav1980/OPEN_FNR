# OPEN FNR Routed Application Foundation Specification

Status: UI-1 foundation  
Date: 2026-05-29  
Related sprint: UI-1 Routed Application Foundation

## 1. Purpose

This document fixes the minimum routed frontend foundation for OPEN FNR.

## 2. Current Implementation

The frontend is implemented in `apps/frontend/src/main.tsx` and uses hash-based workspace routes:

- `#/control-tower`;
- `#/data`;
- `#/forecast`;
- `#/replenishment`;
- `#/operations`;
- `#/admin`;
- `#/process-navigator`.

Runtime service access is centralized in `apps/frontend/src/app_config.ts`.

## 3. Required UI Foundation

| Capability | Requirement |
| --- | --- |
| Routes | Every major workspace has a stable route link. |
| Active route state | Route is derived from `window.location.hash`. |
| API config | API/service URLs are built through `app_config.ts`. |
| Empty/error/loading states | API-backed panels expose fallback or status state. |
| Help footnotes | UI controls can expose help links to specs, tasks and process artifacts. |
| No network hardcode | Host and ports come from frontend env/config. |

## 4. Help Footnote Rule

Every new user-facing UI tool should include contextual help when the action is not self-evident. Help links should point to:

- relevant technical specification;
- business-process specification or BPMN artifact;
- test/evidence report when applicable.

## 5. Acceptance Criteria

UI-1 foundation is accepted when:

- route registry contains all major workspaces;
- Process Navigator route is present;
- frontend config is used for API/service URLs;
- `HelpFootnote` exists and links UI elements to project/process documentation;
- frontend build passes.
