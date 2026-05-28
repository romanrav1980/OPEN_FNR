from fastapi.testclient import TestClient

from open_fnr_api.main import app
from open_fnr_api.replenishment_scale import (
    PARTITIONS,
    BulkRunStatus,
    ReplenishmentPartition,
    bulk_auto_approval_allowed,
)


client = TestClient(app)


def test_industrial_replenishment_run_contains_partitioned_counts() -> None:
    response = client.get("/replenishment-scale/runs")
    assert response.status_code == 200

    run = response.json()["items"][0]
    assert run["run_id"] == "industrial-repl-20260528-001"
    assert run["total_proposals"] == 3_600_000
    assert run["total_projected_stock_rows"] == 108_000_000
    assert run["runtime_minutes"] == 94
    assert run["retention_days"] == 180


def test_bulk_approval_gate_allows_good_partitions() -> None:
    response = client.get("/replenishment-scale/runs/industrial-repl-20260528-001/bulk-gate")
    assert response.status_code == 200

    assert response.json()["bulk_approval_allowed"] is True
    assert bulk_auto_approval_allowed(PARTITIONS, runtime_minutes=94) is True


def test_bulk_approval_requires_replenishment_owner_and_creates_audit_message() -> None:
    denied = client.post(
        "/replenishment-scale/runs/industrial-repl-20260528-001/bulk-approve",
        json={
            "actor": "planner@example.org",
            "actor_role": "Replenishment Planner",
            "saved_filter_id": "north-all-ready",
            "reason": "not allowed",
        },
    )
    allowed = client.post(
        "/replenishment-scale/runs/industrial-repl-20260528-001/bulk-approve",
        json={
            "actor": "owner@example.org",
            "actor_role": "Replenishment Owner",
            "saved_filter_id": "north-all-ready",
            "reason": "Daily high-volume approval.",
        },
    )

    assert denied.status_code == 403
    assert allowed.status_code == 200
    payload = allowed.json()
    assert payload["status"] == "accepted"
    assert payload["accepted_proposals"] == 3_600_000
    assert "north-all-ready" in payload["audit_message"]


def test_export_package_is_async_and_idempotent() -> None:
    response = client.get("/replenishment-scale/runs/industrial-repl-20260528-001/export-package")
    assert response.status_code == 200

    payload = response.json()
    assert payload["status"] == "queued"
    assert payload["target"] == "ERP/WMS"
    assert payload["idempotency_key"] == "industrial-repl-20260528-001:erp-wms:v1"
    assert payload["proposal_count"] == 3_600_000


def test_bulk_approval_gate_blocks_runtime_or_constraint_regression() -> None:
    slow_partition = PARTITIONS[0].model_copy(update={"constraint_eval_ms": 900})
    failed_partition = ReplenishmentPartition(
        partition_id="failed",
        region_id="north",
        category_id="fresh",
        proposal_count=1,
        projected_stock_rows=1,
        constraint_eval_ms=100,
        status=BulkRunStatus.FAILED,
    )

    assert bulk_auto_approval_allowed(PARTITIONS, runtime_minutes=121) is False
    assert bulk_auto_approval_allowed((slow_partition,), runtime_minutes=94) is False
    assert bulk_auto_approval_allowed((failed_partition,), runtime_minutes=94) is False
