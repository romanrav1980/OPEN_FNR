# OPEN FNR ML Training Data Mart And Backtesting Specification

Status: ML-1 foundation  
Date: 2026-05-29  
Related sprint: ML-1 Training Data Mart And Backtesting

## 1. Purpose

This document fixes the ML-1 foundation for production ML work: training dataset snapshots, input source contracts, point-in-time leakage checks and backtesting windows before regular/promo model training is industrialized.

## 2. Backend Scope

| Capability | Endpoint | Requirement |
| --- | --- | --- |
| Training dataset registry | `/ml/training-data/datasets` | Expose dataset id, feature version, data version, history window, scale and input source contracts. |
| Dataset detail | `/ml/training-data/datasets/{dataset_id}` | Return one dataset snapshot or 404. |
| Leakage check | `/ml/training-data/datasets/{dataset_id}/leakage-check` | Validate point-in-time safety and reject history that reaches or exceeds snapshot date. |
| Backtest registry | `/ml/training-data/backtests` | Expose model-vs-baseline metrics, windows, WAPE, Bias and minimum covered weeks. |
| Backtest detail | `/ml/training-data/backtests/{backtest_id}` | Return one backtest or 404. |

## 3. Data Requirements

- Training inputs must include sales history, stock, prices, promo and MDM-derived features.
- Training history must cover 12-24 months where source contracts require it.
- Candidate backtesting must cover at least 26 weeks before production approval.
- Feature snapshots must be point-in-time safe and must not include future actuals.
- Stock-out correction must use only observable state available before the forecast date.

## 4. Test Requirements

| Test class | Required checks |
| --- | --- |
| API tests | Dataset and backtest endpoints return stable contracts. |
| Leakage tests | Future history relative to snapshot date is a blocker. |
| Metric tests | Candidate must beat baseline WAPE and not worsen absolute Bias. |
| Regression tests | Existing forecast/model governance tests remain green. |

## 5. Acceptance Criteria

ML-1 foundation is accepted when:

- training dataset snapshot is available through API;
- input contracts and history windows are visible;
- leakage check is automated;
- backtesting results expose WAPE, Bias and baseline comparison;
- full regression passes.
