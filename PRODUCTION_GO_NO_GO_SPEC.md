# OPEN FNR Production Go/No-Go Specification

Status: PILOT-5 foundation  
Date: 2026-05-29

## 1. Purpose

PILOT-5 records the final production go/no-go decision after pilot evidence is complete. The decision must be based on objective gates and must produce either a launch action or a remediation plan.

## 2. Backend Contract

Go/no-go endpoint:

```text
GET /release-gate/production-go-no-go
```

The response must include:

| Field | Requirement |
| --- | --- |
| `pack_id` | Stable decision pack id |
| `release_candidate_id` | Release candidate under decision |
| `gates` | Final regression, security, DR, business acceptance, controlled export and support handover |
| `unresolved_risks` | Failed gates or blocking risks |
| `sign_off_roles` | Roles required for final launch decision |
| `decision` | `go` or `no_go` |
| `next_action` | Launch pilot expansion or create remediation plan |

## 3. Mandatory Gates

| Gate | Required Evidence |
| --- | --- |
| Final regression | Full automated regression is green |
| Security | OIDC/JWT, RBAC, object access, secrets and audit gates passed |
| DR | Rollback and DR drill evidence accepted |
| Business acceptance | Pilot KPI acceptance pack is accepted |
| Controlled export | Controlled export and reconciliation passed |
| Support handover | Observability, runbooks and incident roles assigned |

## 4. Decision Rules

- If any mandatory gate fails, decision is `no_go`.
- If all mandatory gates pass, decision is `go`.
- A `no_go` decision must produce a remediation plan.
- A `go` decision may launch pilot expansion under the signed release candidate.

## 5. Acceptance Criteria

PILOT-5 is accepted when:

- `/release-gate/production-go-no-go` is available;
- every mandatory gate is visible with owner and evidence;
- failed gates block launch;
- final regression remains green;
- the focused sprint plan is complete.
