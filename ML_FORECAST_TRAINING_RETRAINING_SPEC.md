# OPEN FNR Forecast Training And Retraining Specification

Status: ML-2 foundation  
Date: 2026-05-29  
Related sprint: ML-2 Forecast Training And Retraining

## 1. Purpose

This document fixes the ML-2 foundation for regular demand and promo uplift model training, scheduled retraining and release readiness gates.

## 2. Backend Scope

| Capability | Endpoint | Requirement |
| --- | --- | --- |
| Training runs | `/ml/training/runs` | Expose regular demand and promo uplift model training runs. |
| Training run detail | `/ml/training/runs/{run_id}` | Return one training run or 404. |
| Release readiness | `/ml/training/runs/{run_id}/release-readiness` | Validate 26-week backtesting, WAPE, Bias and fallback availability. |
| Retraining plan | `/ml/training/retraining-plan` | Expose retraining frequency, next run date, trigger policy and runtime budget. |

## 3. Requirements

- Regular demand and promo uplift must be trained as separate model types.
- Candidate release requires at least 26 weeks of backtesting evidence.
- Candidate WAPE must be better than baseline WAPE.
- Candidate absolute Bias must not be worse than baseline absolute Bias.
- Fallback model must be declared before approval.
- Retraining can be scheduled or triggered by drift, WAPE regression or promo bias warning.

## 4. Test Requirements

| Test class | Required checks |
| --- | --- |
| API tests | Training run and retraining plan contracts are stable. |
| Gate tests | Readiness blocks insufficient backtesting, bad WAPE, bad Bias or missing fallback. |
| Regression tests | Existing ML-1, model metadata and governance tests remain green. |

## 5. Acceptance Criteria

ML-2 foundation is accepted when:

- training runs for regular demand and promo uplift are visible through API;
- retraining plan is defined;
- release readiness gates are automated;
- full regression passes.
