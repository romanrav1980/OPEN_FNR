# OPEN FNR Security Access Review Specification

Status: SEC-4 foundation  
Date: 2026-05-29  
Related sprint: SEC-4 Security Audit And Access Review

## 1. Purpose

This document fixes the access review and security audit evidence boundary for OPEN FNR.

## 2. Business Process

Runtime BPMN artifact:

- `processes/security/access_review_process.bpmn20.xml`

Process steps:

1. Access review scheduled.
2. Collect access evidence.
3. Review excessive access.
4. Decide whether remediation is required.
5. Remediate access scope when needed.
6. Write access review audit.
7. Complete review.

## 3. API Boundary

| Endpoint | Purpose |
| --- | --- |
| `GET /security/access-review/report` | Returns access review evidence, excessive access findings and remediation recommendations. |

Only `Security Owner` and `Admin` roles may run the access review report.

## 4. Evidence Model

Each access review item contains:

- user id;
- email;
- roles;
- region scope;
- category scope;
- supplier scope;
- status;
- recommendation;
- evidence strings.

## 5. Acceptance Criteria

SEC-4 foundation is accepted when:

- access review BPMN contains evidence collection, human review, remediation and audit steps;
- access review API denies non-security roles;
- excessive admin access is flagged for review;
- report links to `access_review_process`;
- tests cover API and BPMN structure.
