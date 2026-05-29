# OPEN FNR Audit Retention Runbook

Status: IH-3 baseline  
Date: 2026-05-29

## Purpose

This runbook defines how OPEN FNR retains and purges audit events. Business-process event audit is enabled by default and must remain available for pilot evidence, incident review and compliance checks.

## Configuration

| Setting | Purpose | Default |
| --- | --- | --- |
| `OPEN_FNR_AUDIT_ENABLED` | Enables business audit recording | `true` |
| `OPEN_FNR_AUDIT_RETENTION_DAYS` | Number of days retained before purge eligibility | `1095` |

## API Operations

| Operation | Endpoint | Roles |
| --- | --- | --- |
| Create event | `POST /audit/events` | service/API caller |
| Search events | `GET /audit/events` with filters | authorized API caller |
| Retention plan | `GET /audit/retention-plan` | authorized API caller |
| Purge eligible events | `POST /audit/retention/purge?actor_role=Auditor` | `Admin`, `Auditor` |

## Search Filters

Supported filters:

- `actor`;
- `object_type`;
- `object_id`;
- `event_type`;
- `correlation_id`;
- `limit`.

## Purge Procedure

1. Review `GET /audit/retention-plan`.
2. Confirm `retention_days` matches the active policy.
3. Confirm pilot/legal hold requirements do not block purge.
4. Execute purge only as `Admin` or `Auditor`.
5. Record purge result in the support ticket or release evidence pack.

## Safety Notes

- Application APIs do not expose audit event update.
- Purge deletes only events older than the configured cutoff.
- If legal hold is active, do not run purge; extend `OPEN_FNR_AUDIT_RETENTION_DAYS` or disable the scheduled purge job.
- `.pytest_cache` permission warnings during local tests do not affect audit behavior.
