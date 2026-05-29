# OPEN FNR Security, Admin And Process UI Specification

Status: UI-4 foundation  
Date: 2026-05-29  
Related sprint: UI-4 Security, Admin And Process UI

## 1. Purpose

This document fixes the UI-4 scope for production administration and process operations screens: users, roles, object scope, service accounts, access review, Process Engine task inbox and process deployment governance.

## 2. Functional Scope

| Area | UI capability | Backend contract | Process/audit expectation |
| --- | --- | --- | --- |
| User and role administration | Admin Console lists users, roles, regions, categories and active state | `/security/users` | Admin-only access and audit for changes. |
| Service accounts | Admin Console lists service accounts, scopes, owner role and secret rotation | `/security/service-accounts` | Service accounts are controlled identities with no secrets displayed in UI. |
| Access requests | Access request table and approve/reject/provision actions | `/security/access-requests` | Security Owner approves/rejects, User Manager provisions, every transition is audited. |
| Access review | Access review table shows excessive/privileged access recommendations and evidence | `/security/access-review/report` | Review must be completed before pilot go/no-go. |
| Policy check | Admin Console displays role/object-scope policy status | `/security/policy-check` | Object-level access decisions use shared backend policy helpers. |
| Process operations | Process Engine Task Inbox shows candidate roles, actions and audit history | `/process-engine/*`, `/process-deployment/*` | Human tasks require owner, SLA, permitted action and audit trail. |

## 3. UI Requirements

- Admin and process operations must be reachable from the routed application.
- All API calls must use `apiUrl(...)` and central frontend configuration.
- Service account UI must never display secrets or direct target URLs.
- Access review must expose status, recommendation and evidence per user.
- Process operations must show role assignment, allowed actions, task status and audit timeline.
- BPMN deployment UI must show deployability, runtime strategy and quality gate before runtime upload.

## 4. Business Process Coverage

| Process | Steps visible in UI | Acceptance evidence |
| --- | --- | --- |
| Access request approval | Request, approve/reject, provision, audit. | Access request table and action panel. |
| Access review | Review users, identify excessive access, record recommendation. | Access review status and evidence table. |
| Service account governance | View scopes, owner and secret rotation without exposing secret value. | Service account table. |
| Process task execution | Filter task inbox, perform action, review audit trail. | Process Engine Task Inbox. |
| Process deployment governance | Review artifact counts, deployability, runtime strategy and BPMN quality. | Process deployment cards. |

## 5. Test Requirements

| Test class | Required checks |
| --- | --- |
| UI smoke | Admin Console, Process Engine Task Inbox and process deployment cards are present. |
| API wiring | Security users, access requests, service accounts and access review endpoints are called through `apiUrl(...)`. |
| RBAC | UI exposes denied state, role/object scope and service account policy context. |
| Audit | Access transitions, task actions and deployment gates show audit expectations. |
| Process | BPMN/DMN/CMMN runtime strategy and BPMN quality gate are visible. |
| Accessibility smoke | Admin and process sections have accessible labels. |

## 6. Acceptance Criteria

UI-4 foundation is accepted when:

- admin workflows no longer require direct database inspection for users, service accounts or access review;
- Process Engine task and deployment governance are visible in the routed UI;
- service account secrets remain hidden;
- automated frontend coverage and frontend build pass.
