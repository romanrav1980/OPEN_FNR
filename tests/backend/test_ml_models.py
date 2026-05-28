import pytest
from fastapi.testclient import TestClient

from open_fnr_api.main import app
from open_fnr_api.ml_models import MODEL_VERSIONS, approve_candidate, compare_with_baseline


client = TestClient(app)


def test_model_versions_endpoint_lists_candidate() -> None:
    response = client.get("/ml-models/versions")
    assert response.status_code == 200

    payload = response.json()
    assert payload["total"] == 2
    assert any(item["model_version"] == "lgbm-regular-v1-candidate" for item in payload["items"])


def test_model_comparison_candidate_beats_baseline() -> None:
    response = client.get("/ml-models/versions/lgbm-regular-v1-candidate/comparison")
    assert response.status_code == 200

    payload = response.json()
    assert payload["candidate_better_than_baseline"] is True
    assert payload["fallback_available"] is True
    assert payload["wape_delta"] < 0


def test_model_approval_requires_owner_role() -> None:
    candidate = MODEL_VERSIONS[1]
    with pytest.raises(PermissionError):
        approve_candidate(candidate, "Viewer", "Looks good")


def test_model_approval_records_reason() -> None:
    candidate = MODEL_VERSIONS[1]
    approved = approve_candidate(candidate, "Forecast Owner", "WAPE improved and bias is within threshold")

    assert approved.status == "approved"
    assert approved.approved_by == "Forecast Owner"
    assert approved.approval_reason is not None


def test_model_comparison_function() -> None:
    comparison = compare_with_baseline(MODEL_VERSIONS[1], MODEL_VERSIONS[0])

    assert comparison.candidate_better_than_baseline is True
    assert round(comparison.wape_delta, 3) == -0.026
