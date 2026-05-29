# OPEN FNR Champion Challenger And Drift Specification

Status: ML-3 foundation  
Date: 2026-05-29  
Related sprint: ML-3 Champion Challenger And Drift

## 1. Purpose

This document fixes the ML-3 foundation for model lifecycle governance: champion/challenger registry, shadow scoring, drift reporting, fallback and rollback readiness.

## 2. Backend Scope

| Capability | Endpoint | Requirement |
| --- | --- | --- |
| Candidate list | `/ml-governance/candidates` | Show candidate model metrics and status. |
| Champion/challenger registry | `/ml-governance/registry` | Expose champion, challenger, traffic mode and WAPE comparison. |
| Shadow scoring | `/ml-governance/shadow-reports` | Expose minimum shadow duration and shadow-vs-production WAPE. |
| Drift reports | `/ml-governance/drift-reports` | Expose feature/target drift severity and recommended action. |
| Fallback plans | `/ml-governance/fallback-plans` | Expose fallback model, rollback trigger, rehearsal status and rollback time budget. |
| Release gate | `/ml-governance/candidates/{model_id}/gate` | Block release when WAPE, Bias, drift or shadow metrics fail. |

## 3. Requirements

- Challenger must run in shadow mode before release.
- Minimum shadow duration is 14 days for pilot-critical models.
- Drift severity `high` blocks release.
- Fallback model must be known and rollback rehearsal must pass before production release.
- Rollback must be auditable and executable by Forecast Owner or Data Scientist.

## 4. Test Requirements

| Test class | Required checks |
| --- | --- |
| Registry tests | Champion and challenger are exposed with traffic mode. |
| Shadow tests | Shadow period and shadow WAPE are visible. |
| Drift tests | Drift severity and recommendation are visible. |
| Rollback tests | Fallback plan and rehearsal status are visible. |
| Regression tests | Existing model release/rollback tests remain green. |

## 5. Acceptance Criteria

ML-3 foundation is accepted when:

- champion/challenger registry is available through API;
- shadow and drift reports are available through API;
- fallback and rollback readiness are explicit;
- full regression passes.
