# OPEN FNR Secret Management Specification

Status: SEC-3 foundation  
Date: 2026-05-29  
Related sprint: SEC-3 Secrets And Service Accounts

## 1. Purpose

This document fixes the minimum production boundary for secrets and service accounts.

## 2. Rules

| Rule | Decision |
| --- | --- |
| No secrets in git | Real passwords, private keys, API tokens and local `.env` files are not committed. |
| Examples only | `.env.example` may contain development placeholders only. |
| Runtime injection | STAGE/PROD secrets are injected by deployment runtime or secret files outside git. |
| Service accounts | Integration actions require named service accounts with narrow purpose. |
| Rotation | Service account secrets must have a rotation interval. |
| Audit | Security-sensitive service account use is audited. |

## 3. Service Accounts

Current service account registry is maintained in `apps/backend/open_fnr_api/security.py`.

| Service account | Purpose | Scope |
| --- | --- | --- |
| `svc-airflow-export` | Airflow export to configured DWH/ERP targets | `forecast:read`, `publication:write` |
| `svc-open-fnr-idp-provisioning` | Provision approved access requests in configured IdP/IAM target | `security:provision`, `users:write` |

## 4. Quality Gate

`tests/quality/test_no_committed_secrets.py` checks:

- local `.env` and key files are not committed;
- private key material is absent;
- secret-like assignments are limited to configuration manifests and examples;
- `.gitignore` blocks common secret artifacts.

## 5. Acceptance Criteria

SEC-3 foundation is accepted when:

- `.gitignore` blocks common secret artifacts;
- quality gate prevents committed private keys and local env files;
- service accounts are documented with purpose, scopes and rotation interval;
- production documents require runtime secret injection outside git.
