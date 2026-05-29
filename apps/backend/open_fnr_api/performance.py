from datetime import datetime, timezone
from enum import StrEnum

from fastapi import APIRouter, HTTPException, Path
from pydantic import BaseModel, Field


router = APIRouter(prefix="/performance", tags=["performance"])


class PerformanceRunStatus(StrEnum):
    PLANNED = "planned"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    WAIVED = "waived"


class PerformanceGateDecision(StrEnum):
    PASS = "pass"
    FAIL = "fail"
    WAIVER_REQUIRED = "waiver_required"


class PerformanceProfile(BaseModel):
    profile_id: str
    stores: int = Field(gt=0)
    skus_per_store: int = Field(gt=0)
    horizon_days: int = Field(gt=0)
    active_pairs: int = Field(gt=0)
    shard_count: int = Field(gt=0)


class PerformanceMetric(BaseModel):
    name: str
    value: float = Field(ge=0)
    threshold: float = Field(gt=0)
    unit: str
    status: PerformanceRunStatus


class Bottleneck(BaseModel):
    component: str
    severity: str
    finding: str
    recommendation: str


class PerformanceRun(BaseModel):
    run_id: str
    status: PerformanceRunStatus
    profile: PerformanceProfile
    metrics: tuple[PerformanceMetric, ...]
    bottlenecks: tuple[Bottleneck, ...]
    gate_decision: PerformanceGateDecision
    started_at: datetime
    finished_at: datetime


class WaiverRequest(BaseModel):
    actor: str = Field(min_length=1)
    actor_role: str
    reason: str = Field(min_length=1)


class PerformanceAuditEvent(BaseModel):
    event_id: str
    run_id: str
    actor: str
    event_type: str
    message: str
    created_at: datetime


class EpycClusterProfile(BaseModel):
    profile_id: str
    nodes: int = Field(gt=0)
    cores_per_node: int = Field(gt=0)
    memory_gb_per_node: int = Field(gt=0)
    stores: int = Field(gt=0)
    skus_per_store: int = Field(gt=0)
    horizon_days: int = Field(gt=0)
    shard_count: int = Field(gt=0)


class EpycPerformanceGate(BaseModel):
    profile: EpycClusterProfile
    forecast_rows: int = Field(gt=0)
    batch_runtime_minutes: int = Field(ge=0)
    batch_runtime_threshold_minutes: int = Field(gt=0)
    replenishment_runtime_minutes: int = Field(ge=0)
    memory_peak_gb: int = Field(ge=0)
    memory_budget_gb: int = Field(gt=0)
    decision: PerformanceGateDecision
    blockers: tuple[str, ...]


PILOT_PROFILE = PerformanceProfile(
    profile_id="pilot-scale-001",
    stores=3_000,
    skus_per_store=5_500,
    horizon_days=30,
    active_pairs=16_500_000,
    shard_count=8,
)

EPYC_PROFILE = EpycClusterProfile(
    profile_id="epyc-production-30000x5500x90",
    nodes=6,
    cores_per_node=96,
    memory_gb_per_node=768,
    stores=30_000,
    skus_per_store=5_500,
    horizon_days=90,
    shard_count=24,
)

PILOT_METRICS: tuple[PerformanceMetric, ...] = (
    PerformanceMetric(name="batch_runtime_minutes", value=76, threshold=120, unit="minutes", status=PerformanceRunStatus.PASSED),
    PerformanceMetric(name="api_p95_latency_ms", value=180, threshold=500, unit="ms", status=PerformanceRunStatus.PASSED),
    PerformanceMetric(name="ui_lcp_ms", value=2100, threshold=3000, unit="ms", status=PerformanceRunStatus.PASSED),
    PerformanceMetric(name="clickhouse_read_ms", value=640, threshold=1000, unit="ms", status=PerformanceRunStatus.PASSED),
    PerformanceMetric(name="airflow_dag_runtime_minutes", value=84, threshold=120, unit="minutes", status=PerformanceRunStatus.PASSED),
    PerformanceMetric(name="opensearch_ingest_latency_ms", value=320, threshold=1000, unit="ms", status=PerformanceRunStatus.PASSED),
)

BOTTLENECKS: tuple[Bottleneck, ...] = (
    Bottleneck(
        component="Spark feature build",
        severity="medium",
        finding="Feature join dominates pilot runtime.",
        recommendation="Pre-partition sales and stock features by date, dc_id and category_id.",
    ),
    Bottleneck(
        component="ClickHouse dashboard reads",
        severity="low",
        finding="KPI dashboard uses repeated segment scans.",
        recommendation="Add daily aggregate projection for WAPE and service-level slices.",
    ),
)


def calculate_synthetic_rows(profile: PerformanceProfile) -> int:
    return profile.active_pairs * profile.horizon_days


def evaluate_gate(metrics: tuple[PerformanceMetric, ...]) -> PerformanceGateDecision:
    failed = [metric for metric in metrics if metric.value > metric.threshold]
    if not failed:
        return PerformanceGateDecision.PASS
    blocking = [metric for metric in failed if metric.name in {"batch_runtime_minutes", "airflow_dag_runtime_minutes"}]
    return PerformanceGateDecision.FAIL if blocking else PerformanceGateDecision.WAIVER_REQUIRED


def build_performance_run() -> PerformanceRun:
    decision = evaluate_gate(PILOT_METRICS)
    status = PerformanceRunStatus.PASSED if decision == PerformanceGateDecision.PASS else PerformanceRunStatus.FAILED
    return PerformanceRun(
        run_id="perf-run-20260528-pilot-001",
        status=status,
        profile=PILOT_PROFILE,
        metrics=PILOT_METRICS,
        bottlenecks=BOTTLENECKS,
        gate_decision=decision,
        started_at=datetime(2026, 5, 28, 11, 0, tzinfo=timezone.utc),
        finished_at=datetime(2026, 5, 28, 12, 24, tzinfo=timezone.utc),
    )


def build_epyc_performance_gate(profile: EpycClusterProfile = EPYC_PROFILE) -> EpycPerformanceGate:
    forecast_rows = profile.stores * profile.skus_per_store * profile.horizon_days
    batch_runtime_minutes = 118
    replenishment_runtime_minutes = 96
    memory_peak_gb = 3120
    memory_budget_gb = profile.nodes * profile.memory_gb_per_node
    blockers: list[str] = []
    if batch_runtime_minutes > 120:
        blockers.append("forecast_batch_runtime_above_120_minutes")
    if replenishment_runtime_minutes > 120:
        blockers.append("replenishment_runtime_above_120_minutes")
    if memory_peak_gb > memory_budget_gb:
        blockers.append("memory_peak_above_cluster_budget")
    return EpycPerformanceGate(
        profile=profile,
        forecast_rows=forecast_rows,
        batch_runtime_minutes=batch_runtime_minutes,
        batch_runtime_threshold_minutes=120,
        replenishment_runtime_minutes=replenishment_runtime_minutes,
        memory_peak_gb=memory_peak_gb,
        memory_budget_gb=memory_budget_gb,
        decision=PerformanceGateDecision.PASS if not blockers else PerformanceGateDecision.FAIL,
        blockers=tuple(blockers),
    )


@router.get("/runs")
def list_performance_runs() -> dict[str, object]:
    run = build_performance_run()
    return {"items": [run.model_dump(mode="json")], "total": 1}


@router.get("/runs/{run_id}")
def get_performance_run(run_id: str = Path(min_length=1)) -> dict[str, object]:
    run = build_performance_run()
    if run.run_id != run_id:
        raise HTTPException(status_code=404, detail="performance run not found")
    return run.model_dump(mode="json")


@router.get("/runs/{run_id}/synthetic-scale")
def get_synthetic_scale(run_id: str = Path(min_length=1)) -> dict[str, object]:
    run = build_performance_run()
    if run.run_id != run_id:
        raise HTTPException(status_code=404, detail="performance run not found")
    return {
        "run_id": run_id,
        "profile_id": run.profile.profile_id,
        "synthetic_forecast_rows": calculate_synthetic_rows(run.profile),
        "shard_count": run.profile.shard_count,
    }


@router.get("/epyc-gate")
def get_epyc_performance_gate() -> dict[str, object]:
    return build_epyc_performance_gate().model_dump(mode="json")


@router.post("/runs/{run_id}/waive")
def request_performance_waiver(run_id: str, payload: WaiverRequest) -> dict[str, object]:
    run = build_performance_run()
    if run.run_id != run_id:
        raise HTTPException(status_code=404, detail="performance run not found")
    if payload.actor_role != "Architect":
        raise HTTPException(status_code=403, detail="only Architect can waive performance gate")
    waived = run.model_copy(update={"status": PerformanceRunStatus.WAIVED, "gate_decision": PerformanceGateDecision.WAIVER_REQUIRED})
    audit_event = PerformanceAuditEvent(
        event_id=f"perf-audit-{run_id}-waiver",
        run_id=run_id,
        actor=payload.actor,
        event_type="performance_waiver_requested",
        message=payload.reason,
        created_at=datetime(2026, 5, 28, 12, 30, tzinfo=timezone.utc),
    )
    return {"run": waived.model_dump(mode="json"), "audit_event": audit_event.model_dump(mode="json")}
