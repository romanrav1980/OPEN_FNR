# OPEN FNR EPYC Performance Gate Specification

Status: ML-5 foundation  
Date: 2026-05-29  
Related sprint: ML-5 EPYC Performance Gate

## 1. Purpose

This document fixes the ML-5 foundation for validating production-scale forecast and replenishment runtime on the accepted AMD EPYC cluster profile.

## 2. Target Profile

| Parameter | Value |
| --- | --- |
| Stores | 30 000 |
| SKU per store | 5 500 |
| Forecast horizon | 90 days |
| Forecast rows | 14 850 000 000 |
| Cluster nodes | 6 |
| Cores per node | 96 |
| RAM per node | 768 GB |
| Shards | 24 |

## 3. Backend Scope

| Capability | Endpoint | Requirement |
| --- | --- | --- |
| EPYC performance gate | `/performance/epyc-gate` | Expose volume, runtime, memory budget and pass/fail decision. |

## 4. Requirements

- Forecast batch runtime must be no more than 120 minutes.
- Replenishment optimization runtime must be no more than 120 minutes.
- Memory peak must remain below cluster memory budget.
- Gate must expose blockers explicitly.
- Gate must not depend on hardcoded host, port or service URL.

## 5. Acceptance Criteria

ML-5 foundation is accepted when:

- EPYC production profile is available through API;
- forecast row count matches 30 000 x 5 500 x 90;
- performance gate blocks insufficient memory profile;
- full regression passes.
