from datetime import date

from fastapi.testclient import TestClient

from open_fnr_api.main import app
from open_fnr_api.ml_training import BACKTEST_RESULTS, TRAINING_DATASETS, backtest_better_than_baseline, detect_point_in_time_leakage


client = TestClient(app)


def test_training_dataset_endpoint_exposes_real_input_contracts() -> None:
    response = client.get("/ml/training-data/datasets")
    assert response.status_code == 200
    payload = response.json()

    dataset = payload["items"][0]
    contracts = {item["contract_name"] for item in dataset["input_sources"]}
    assert dataset["dataset_id"] == "training-snapshot-20260528-001"
    assert dataset["status"] == "ready"
    assert dataset["history_start"] == "2024-05-28"
    assert {"pos_sales_line", "dwh_sales_history_line", "wms_stock_snapshot_line", "erp_price_line", "promo_plan_line"} <= contracts


def test_training_dataset_leakage_check_blocks_future_history() -> None:
    dataset = TRAINING_DATASETS[0]
    clean = detect_point_in_time_leakage(dataset)
    assert clean.gate == "pass"
    assert clean.blockers == ()

    bad = dataset.model_copy(update={"history_end": date(2026, 5, 28)})
    failed = detect_point_in_time_leakage(bad)
    assert failed.gate == "blocker"
    assert "history_end_must_be_before_snapshot_date" in failed.blockers


def test_backtest_endpoint_exposes_windows_and_baseline_comparison() -> None:
    response = client.get("/ml/training-data/backtests")
    assert response.status_code == 200
    payload = response.json()

    result = payload["items"][0]
    assert result["backtest_id"] == "backtest-lgbm-regular-v1-20260528"
    assert result["dataset_id"] == "training-snapshot-20260528-001"
    assert result["min_weeks_covered"] >= 26
    assert result["better_than_baseline"] is True
    assert len(result["windows"]) >= 3


def test_backtest_better_than_baseline_requires_wape_and_bias_improvement() -> None:
    good = BACKTEST_RESULTS[0]
    assert backtest_better_than_baseline(good) is True

    bad_wape = good.model_copy(update={"wape": 0.2})
    assert backtest_better_than_baseline(bad_wape) is False

    bad_bias = good.model_copy(update={"bias": 0.02})
    assert backtest_better_than_baseline(bad_bias) is False
