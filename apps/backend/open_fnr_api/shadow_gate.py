from __future__ import annotations

from datetime import date, datetime, timedelta, timezone

from fastapi import APIRouter
from pydantic import BaseModel, Field

from .audit import AuditEventCreate, record_audit_event_if_enabled
from .data_quality import run_source_contract_dq
from .shadow_load import ShadowLoadReport, run_shadow_load_discovery


router = APIRouter(prefix="/data/ingestion/shadow-load", tags=["data-ingestion"])


class ShadowLoadGateRequest(BaseModel):
    business_date: date
    actor: str = Field(min_length=1, max_length=128)
    actor_role: str = Field(default="Data Engineer", min_length=1, max_length=64)
    landing_root_path: str | None = Field(default=None, max_length=512)


class ShadowLoadRecoveryTask(BaseModel):
    task_id: str
    process_key: str = "source_batch_publication_process"
    case_key: str = "source_batch_recovery_case"
    business_key: str
    name: str
    assigned_role: str
    status: str = "open"
    sla_due_at: datetime
    reason: str
    available_actions: tuple[str, ...] = ("request_resend", "approve_reprocessing", "waive", "comment")


class ShadowLoadGateResponse(BaseModel):
    process_instance_id: str
    business_date: date
    status: str
    report: ShadowLoadReport
    recovery_tasks: tuple[ShadowLoadRecoveryTask, ...]
    audit_recorded: bool


def owner_role_for_source(source_system: str) -> str:
    return {
        "POS": "Data Engineer",
        "DWH": "Sales Data Owner",
        "WMS": "Supply Chain Data Owner",
        "ERP": "Integration Owner",
        "MDM": "MDM Data Owner",
        "PROMO": "Promo Planner",
    }.get(source_system.upper(), "Data Owner")


def build_recovery_tasks(report: ShadowLoadReport) -> tuple[ShadowLoadRecoveryTask, ...]:
    due_at = datetime.now(timezone.utc) + timedelta(hours=4)
    tasks: list[ShadowLoadRecoveryTask] = []
    for result in report.results:
        if result.status != "missing_files":
            continue
        business_key = f"{result.source_system}:{result.contract_name}:{result.business_date.isoformat()}"
        tasks.append(
            ShadowLoadRecoveryTask(
                task_id=f"task-shadow-load-{result.source_system.lower()}-{result.contract_name}",
                business_key=business_key,
                name=f"Recover missing source files for {result.source_system} / {result.contract_name}",
                assigned_role=owner_role_for_source(result.source_system),
                sla_due_at=due_at,
                reason="missing_files",
            )
        )
    return tuple(tasks)


def build_dq_recovery_tasks(report: ShadowLoadReport) -> tuple[ShadowLoadRecoveryTask, ...]:
    dq_result = run_source_contract_dq(report)
    due_at = datetime.now(timezone.utc) + timedelta(hours=4)
    tasks: list[ShadowLoadRecoveryTask] = []
    for result in dq_result.results:
        if result.blocker_count == 0:
            continue
        business_key = f"{result.source_system}:{result.contract_name}:{report.business_date.isoformat()}"
        tasks.append(
            ShadowLoadRecoveryTask(
                task_id=f"task-dq-blocker-{result.source_system.lower()}-{result.contract_name}",
                business_key=business_key,
                name=f"Resolve DQ blocker for {result.source_system} / {result.contract_name}",
                assigned_role=owner_role_for_source(result.source_system),
                sla_due_at=due_at,
                reason="dq_blocker",
                available_actions=("fix_source", "request_resend", "approve_waiver", "comment"),
            )
        )
    return tuple(tasks)


@router.post("/run")
def run_shadow_load_gate(request: ShadowLoadGateRequest) -> dict[str, object]:
    report = run_shadow_load_discovery(request.business_date, request.landing_root_path)
    recovery_tasks = build_recovery_tasks(report)
    dq_recovery_tasks = build_dq_recovery_tasks(report) if not recovery_tasks else ()
    all_recovery_tasks = recovery_tasks + dq_recovery_tasks
    process_instance_id = f"proc-shadow-load-{request.business_date.isoformat()}"
    event = record_audit_event_if_enabled(
        AuditEventCreate(
            event_type="shadow_load_gate_run",
            actor=request.actor,
            actor_role=request.actor_role,
            object_type="source_batch",
            object_id=process_instance_id,
            action="run_shadow_load_gate",
            reason=f"status={report.status}; missing_contracts={report.missing_contracts}; recovery_tasks={len(all_recovery_tasks)}",
            correlation_id=process_instance_id,
            payload={
                "business_date": request.business_date.isoformat(),
                "landing_root_path": report.landing_root_path,
                "status": report.status,
                "missing_contracts": report.missing_contracts,
                "recovery_tasks": len(all_recovery_tasks),
            },
        )
    )

    response = ShadowLoadGateResponse(
        process_instance_id=process_instance_id,
        business_date=request.business_date,
        status="recovery_required" if all_recovery_tasks else "ready_for_validation",
        report=report,
        recovery_tasks=all_recovery_tasks,
        audit_recorded=event is not None,
    )
    return response.model_dump(mode="json")
