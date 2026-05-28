from fastapi.testclient import TestClient

from open_fnr_api.main import app


client = TestClient(app)


def test_active_matrix_summary_returns_totals() -> None:
    response = client.get("/feature-mart/active-matrix")
    assert response.status_code == 200

    payload = response.json()
    assert payload["total"] == 2
    assert payload["active_pairs_total"] == 2140000


def test_feature_definitions_are_point_in_time_safe() -> None:
    response = client.get("/feature-mart/features")
    assert response.status_code == 200

    payload = response.json()
    assert payload["point_in_time_safe"] is True
    assert {item["feature_group"] for item in payload["items"]} >= {"lag", "rolling", "price", "stock"}


def test_feature_version_detail() -> None:
    response = client.get("/feature-mart/versions/fm-20260528-001")
    assert response.status_code == 200
    assert response.json()["status"] == "published"


def test_feature_version_unknown_returns_404() -> None:
    response = client.get("/feature-mart/versions/missing")
    assert response.status_code == 404
