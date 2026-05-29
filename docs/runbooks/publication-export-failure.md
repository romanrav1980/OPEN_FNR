# Publication Export Failure Runbook

Status: DEP-3 foundation  
Date: 2026-05-29  
Incident type: `publication_export_failed`

## Annotation

This runbook is used to test and recover a failed ERP/WMS/DWH publication export. The goal is to restore export flow without duplicate orders, duplicate replenishment publication or silent data loss.

## Symptoms

| Signal | Expected Evidence |
| --- | --- |
| Alert | `alert-rule-publication-export-failed` or `alert-export-20260528-001` |
| Incident | Open incident linked to publication export |
| Logs | Log row contains `trace_id` and export package id |
| Process | Publication process or incident management process is active |
| Business impact | ERP or auto-order export is delayed |

## Step-by-Step Recovery

| Step | What To Do | Why | Expected Result |
| --- | --- | --- | --- |
| 1 | Confirm alert severity and owner role in `/observability/alerts`. | Ensures the correct SLA and escalation path are applied. | SEV2 alert is owned by integration support. |
| 2 | Open `/observability/logs/search` with the export error text or trace id. | Finds technical evidence and correlated service logs. | Log result contains the failing export trace id. |
| 3 | Check publication package id and idempotency key in the publication console or API evidence. | Prevents duplicate export after retry. | Idempotency key is present and stable. |
| 4 | Retry only through the approved publication retry action. | Keeps audit trail and retry policy consistent. | Export retry is created or rejected with explicit reason. |
| 5 | If retry fails, escalate incident to Integration Lead. | Moves the incident to the accountable support level. | Incident status becomes escalated. |
| 6 | Resolve only after export status is successful or business owner accepts degraded mode. | Avoids closing an active business impact. | Incident timeline contains recovery evidence. |

## Escalation

| Condition | Escalate To |
| --- | --- |
| Retry budget exhausted | Integration Lead |
| ERP target unavailable | IT Operations Lead |
| Duplicate export risk detected | Incident Manager |
| Business deadline breached | Replenishment Lead |

## Closure Evidence

The incident can be resolved only when the operator records:

- alert id;
- incident id;
- export package id;
- trace id;
- retry result;
- duplicate-publication guard result.
