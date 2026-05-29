# ML-1 Completion Context

Date: 2026-05-29  
Sprint: ML-1 Training Data Mart And Backtesting  
Status: completed foundation

## What Was Completed

- Added `apps/backend/open_fnr_api/ml_training.py`.
- Added `/ml/training-data/datasets`, `/ml/training-data/datasets/{dataset_id}`, `/ml/training-data/datasets/{dataset_id}/leakage-check`, `/ml/training-data/backtests` and `/ml/training-data/backtests/{backtest_id}`.
- Added point-in-time leakage check and model-vs-baseline backtest comparison helper.
- Added `ML_TRAINING_BACKTESTING_SPEC.md`.
- Added backend tests in `tests/backend/test_ml_training.py`.

## Verification

- `pytest tests/backend/test_ml_training.py tests/backend/test_ml_models.py tests/backend/test_ml_governance.py tests/quality/test_text_encoding.py tests/quality/test_no_hardcoded_network_config.py`
- Full regression: 546 automated tests passed.

## Remaining ML Work

- ML-2 Forecast Training And Retraining.
- ML-3 Champion Challenger And Drift.
- ML-4 Replenishment Optimization Production.
- ML-5 EPYC Performance Gate.
