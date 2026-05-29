from statistics import quantiles
from time import perf_counter

from fastapi.testclient import TestClient

from open_fnr_api.main import app


client = TestClient(app)


def _measure_get(path: str, params: dict[str, object] | None = None, samples: int = 25) -> list[float]:
    durations: list[float] = []
    for _ in range(samples):
        started = perf_counter()
        response = client.get(path, params=params)
        durations.append(perf_counter() - started)
        assert response.status_code == 200
    return durations


def _p95_seconds(durations: list[float]) -> float:
    return quantiles(durations, n=20)[18]


def test_process_navigator_map_endpoint_keeps_interactive_p95() -> None:
    durations = _measure_get("/process-navigator/map", {"zoom": 1, "env": "test"})

    assert _p95_seconds(durations) < 0.50


def test_process_navigator_detail_endpoints_keep_interactive_p95() -> None:
    endpoints = (
        "/process-navigator/processes/forecast_review_process/drilldown",
        "/process-navigator/processes/forecast_review_process/performance",
        "/process-navigator/processes/forecast_review_process/versions",
        "/process-navigator/infrastructure/health",
    )

    for endpoint in endpoints:
        durations = _measure_get(endpoint, {"env": "test"}, samples=15)
        assert _p95_seconds(durations) < 0.50
