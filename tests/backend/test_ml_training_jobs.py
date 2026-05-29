from fastapi.testclient import TestClient

from open_fnr_api.main import app
from open_fnr_api.ml_training_jobs import TRAINING_RUNS, release_readiness


client = TestClient(app)


def test_training_runs_endpoint_covers_regular_and_promo_models() -> None:
    response = client.get("/ml/training/runs")
    assert response.status_code == 200
    payload = response.json()

    model_types = {item["model_type"] for item in payload["items"]}
    assert {"regular_demand", "promo_uplift"} <= model_types
    assert payload["total"] == 2


def test_retraining_plan_endpoint_defines_scheduled_policy() -> None:
    response = client.get("/ml/training/retraining-plan")
    assert response.status_code == 200
    payload = response.json()

    regular = next(item for item in payload["items"] if item["model_type"] == "regular_demand")
    assert regular["frequency"] == "weekly"
    assert regular["trigger_policy"] == "scheduled_or_drift_warning_or_wape_regression"
    assert regular["max_training_runtime_minutes"] <= 90


def test_training_release_readiness_requires_backtesting_wape_bias_and_fallback() -> None:
    run = TRAINING_RUNS[0]
    readiness = release_readiness(run)
    assert readiness.ready is True
    assert readiness.blockers == ()

    short_backtest = run.model_copy(update={"metrics": run.metrics.model_copy(update={"backtesting_weeks": 12})})
    assert "backtesting_window_below_26_weeks" in release_readiness(short_backtest).blockers

    bad_wape = run.model_copy(update={"metrics": run.metrics.model_copy(update={"wape": 0.2})})
    assert "candidate_wape_not_better_than_baseline" in release_readiness(bad_wape).blockers

    no_fallback = run.model_copy(update={"fallback_model_version": ""})
    assert "fallback_model_missing" in release_readiness(no_fallback).blockers


def test_training_release_readiness_endpoint() -> None:
    response = client.get("/ml/training/runs/train-regular-lgbm-20260528-001/release-readiness")
    assert response.status_code == 200
    payload = response.json()

    assert payload["ready"] is True
    assert "wape_better_than_baseline" in payload["gates"]
