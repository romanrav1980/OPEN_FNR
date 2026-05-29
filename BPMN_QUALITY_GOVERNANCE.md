# OPEN FNR BPMN Quality Governance

Date: 2026-05-29
Status: mandatory process quality gate.

## Purpose

BPMN quality must be checked cognitively, not only technically. A process is not production-ready just because it is valid XML or can be deployed to Flowable. It must also make business sense, expose meaningful alternatives, avoid dead-end work, and make human ownership, SLA and audit expectations visible for review.

## Blocking Rules

| Check | Severity | Rationale |
| --- | --- | --- |
| Exactly one start event | blocker | A business process must have one clear trigger |
| At least one end event | blocker | Every process needs explicit terminal outcomes |
| No duplicate BPMN ids | blocker | Duplicate ids make audit and runtime behavior ambiguous |
| All sequence flows reference existing nodes | blocker | Broken references indicate an invalid process graph |
| Every non-start node has incoming flow | blocker | No unreachable business steps |
| Every non-end node has outgoing flow | blocker | No dead-end work items |
| Every node can reach an end event | blocker | No process branch may trap work forever |
| Question gateways have at least two outgoing paths | blocker | A business decision must have meaningful alternatives |

## Cognitive Challenge Rules

| Challenge | Review question |
| --- | --- |
| Human task role/SLA/audit | Who owns the task, what SLA applies, where is escalation, how is action audited? |
| Manual decision without visible audit step | Is audit handled by Flowable listener, backend event or explicit service task? |
| Exception path | Does the model show rejected, blocked, degraded or escalated outcomes explicitly? |
| Best-practice fit | Does the workflow reduce planner load, avoid hidden work and keep accountability clear? |

## Operational Gate

API endpoint:

```text
GET /process-deployment/packages/current/bpmn-quality
```

Regression:

```text
tests/backend/test_process_deployment.py
```

Release rule:

- `blocker_count` must be `0`.
- `quality_gate` must be `passed`.
- Cognitive challenges must be reviewed before production sign-off.

## Current Finding And Repair

The first cognitive scan found two one-way question gateways:

- `processes/diagnostics/diagnostic_insight_review_process.bpmn20.xml`
- `processes/supplier-collaboration/supplier_collaboration_process.bpmn20.xml`

Both were repaired by adding explicit alternative paths.
