from fastapi.testclient import TestClient

from open_fnr_api.data_scale import (
    LINEAGE,
    PARTITIONS,
    DqGateDecision,
    PartitionHealth,
    PartitionStatus,
    evaluate_industrial_dq_gate,
    validate_lineage_completeness,
)
from open_fnr_api.main import app


client = TestClient(app)


def test_data_volume_profile_matches_industrial_scale() -> None:
    response = client.get("/data-scale/profile")
    assert response.status_code == 200

    payload = response.json()
    assert payload["stores"] == 30000
    assert payload["skus"] == 5500
    assert payload["history_days"] == 730
    assert payload["forecast_horizon_days"] == 90
    assert payload["expected_fact_rows"] == 120_450_000_000


def test_partition_health_requires_data_platform_owner() -> None:
    denied = client.get("/data-scale/partitions", params={"actor_role": "Viewer"})
    allowed = client.get("/data-scale/partitions", params={"actor_role": "Data Platform Owner"})

    assert denied.status_code == 403
    assert allowed.status_code == 200
    assert allowed.json()["total"] == 2


def test_lineage_is_complete_and_links_raw_clean_mart() -> None:
    response = client.get("/data-scale/lineage")
    assert response.status_code == 200

    payload = response.json()
    assert payload["complete"] is True
    assert payload["items"][0]["source"] == "POS.raw_sales"
    assert payload["items"][-1]["target"] == "mart.feature_store"


def test_industrial_dq_gate_pass_warning_and_block() -> None:
    late_partition = (
        PartitionHealth(
            partition_id="late",
            domain="sales",
            business_date="2026-05-28",
            row_count=100,
            expected_min_rows=1000,
            status=PartitionStatus.LATE,
            freshness_minutes=120,
            lineage_source="POS",
        ),
    )
    failed_partition = (
        late_partition[0].model_copy(update={"status": PartitionStatus.FAILED}),
    )

    assert evaluate_industrial_dq_gate(PARTITIONS) == DqGateDecision.PASS
    assert evaluate_industrial_dq_gate(late_partition) == DqGateDecision.WARNING
    assert evaluate_industrial_dq_gate(failed_partition) == DqGateDecision.BLOCK


def test_lineage_completeness_helper_detects_missing_source() -> None:
    assert validate_lineage_completeness(LINEAGE) is True
    assert validate_lineage_completeness(LINEAGE[:1]) is False
