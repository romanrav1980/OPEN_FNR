# OPEN FNR Replenishment Optimization Production Specification

Status: ML-4 foundation  
Date: 2026-05-29  
Related sprint: ML-4 Replenishment Optimization Production

## 1. Purpose

This document fixes the ML-4 foundation for production replenishment optimization: service-level targets by ABC/XYZ segment, safety stock calculation, projected stock, order proposal generation and fresh waste impact gates.

## 2. Backend Scope

| Capability | Endpoint | Requirement |
| --- | --- | --- |
| Service-level targets | `/replenishment/optimization/service-level-targets` | Expose 9-cell ABC/XYZ matrix with target service level and safety stock z-score. |
| Optimization runs | `/replenishment/optimization/runs` | Expose projected stock rows, order proposal rows, fresh rows and business impacts. |
| Export gate | `/replenishment/optimization/runs/{run_id}/gate` | Block export when source readiness, projected stock or order proposals are missing. |

## 3. Requirements

- ABC/XYZ segment must drive service-level target and safety-stock z-score.
- Safety stock must scale with demand variability and lead time.
- Optimization run must expose service level, stock cost and waste impact.
- Export gate must block if source readiness is not ready.
- Export gate must block if projected stock or order proposals are missing.
- Fresh waste impact must be calculated for fresh categories in pilot scope.

## 4. Test Requirements

| Test class | Required checks |
| --- | --- |
| Segment tests | ABC/XYZ 9-cell matrix exists. |
| Formula tests | Safety stock uses z-score and lead time. |
| Gate tests | Missing source readiness, projected stock or order proposals block export. |
| Business impact tests | Service level, stock cost and waste impact are exposed. |
| Regression tests | Existing replenishment/fresh tests remain green. |

## 5. Acceptance Criteria

ML-4 foundation is accepted when:

- service-level targets are available through API;
- replenishment optimization run is available through API;
- export readiness gate is automated;
- full regression passes.
