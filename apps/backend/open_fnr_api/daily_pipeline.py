from __future__ import annotations

from datetime import date
from enum import StrEnum

from fastapi import APIRouter
from pydantic import BaseModel, Field

from .audit import AuditEventCreate, record_audit_event_if_enabled
from .clean_publication import CleanPublicationRunMode, clean_publication_plans_for_date, execute_clean_publication_plan
from .data_quality import run_source_contract_dq
from .feature_mart import FeatureBuildMode, FeatureBuildStatus, feature_build_plan_for_date
from .shadow_load import run_shadow_load_discovery


class DailyPipelineStageStatus(StrEnum):
    PASSED = "passed"
    READY = "ready"
    BLOCKED = "blocked"
    SKIPPED = "skipped"


class DailyPipelineGateRequest(BaseModel):
    business_date: date
    actor: str = Field(min_length=1, max_length=128)
    actor_role: str = Field(default="Data Platform Owner", min_length=1, max_length=64)
    landing_root_path: str | None = Field(default=None, max_length=512)
    feature_build_mode: FeatureBuildMode = FeatureBuildMode.DRY_RUN


class DailyPipelineStage(BaseModel):
    stage_key: str = Field(min_length=1, max_length=128)
    name: str = Field(min_length=1, max_length=255)
    status: DailyPipelineStageStatus
    owner_role: str = Field(min_length=1, max_length=64)
    process_key: str = Field(min_length=1, max_length=128)
    task_id: str | None = Field(default=None, max_length=128)
    details: str = Field(min_length=1, max_length=1024)


class DailyPipelineGateResponse(BaseModel):
    run_id: str
    business_date: date
    status: str
    stages: tuple[DailyPipelineStage, ...]
    audit_recorded: bool


router = APIRouter(prefix="/pipeline/daily-gate", tags=["pipeline"])


def run_daily_pipeline_gate(request: DailyPipelineGateRequest) -> DailyPipelineGateResponse:
    stages: list[DailyPipelineStage] = []
    shadow_report = run_shadow_load_discovery(request.business_date, request.landing_root_path)
    shadow_passed = shadow_report.status == "ready_for_validation"
    stages.append(
        DailyPipelineStage(
            stage_key="shadow_load",
            name="Shadow-load source discovery",
            status=DailyPipelineStageStatus.PASSED if shadow_passed else DailyPipelineStageStatus.BLOCKED,
            owner_role="Data Engineer",
            process_key="source_batch_publication_process",
            task_id=None if shadow_passed else "source_batch_recovery_case",
            details=(
                f"discovered={shadow_report.discovered_contracts}; "
                f"missing={shadow_report.missing_contracts}; total={shadow_report.total_contracts}"
            ),
        )
    )

    dq_result = run_source_contract_dq(shadow_report)
    dq_passed = dq_result.status == "passed"
    stages.append(
        DailyPipelineStage(
            stage_key="source_contract_dq",
            name="Source contract DQ",
            status=DailyPipelineStageStatus.PASSED if dq_passed else DailyPipelineStageStatus.BLOCKED,
            owner_role="Data Platform Owner",
            process_key="source_batch_publication_process",
            task_id=None if dq_passed else "source_batch_recovery_case",
            details=f"status={dq_result.status}; blockers={dq_result.blocker_count}; warnings={dq_result.warning_count}",
        )
    )

    if dq_passed:
        clean_plans = clean_publication_plans_for_date(request.business_date)
        clean_results = tuple(
            execute_clean_publication_plan(plan, CleanPublicationRunMode.DRY_RUN) for plan in clean_plans
        )
        clean_ready = all(result.status == "validated" for result in clean_results)
        stages.append(
            DailyPipelineStage(
                stage_key="clean_publication",
                name="Clean canonical publication dry-run",
                status=DailyPipelineStageStatus.READY if clean_ready else DailyPipelineStageStatus.BLOCKED,
                owner_role="Data Platform Owner",
                process_key="source_batch_publication_process",
                task_id="task-clean-publication-001",
                details=f"plans={len(clean_plans)}; mode={CleanPublicationRunMode.DRY_RUN.value}",
            )
        )
    else:
        clean_ready = False
        stages.append(
            DailyPipelineStage(
                stage_key="clean_publication",
                name="Clean canonical publication dry-run",
                status=DailyPipelineStageStatus.SKIPPED,
                owner_role="Data Platform Owner",
                process_key="source_batch_publication_process",
                task_id="task-clean-publication-001",
                details="Skipped because source contract DQ is blocked.",
            )
        )

    if clean_ready:
        feature_plan = feature_build_plan_for_date(request.business_date)
        feature_status = (
            FeatureBuildStatus.VALIDATED
            if request.feature_build_mode == FeatureBuildMode.DRY_RUN
            else FeatureBuildStatus.PUBLISHED
        )
        stages.append(
            DailyPipelineStage(
                stage_key="feature_build",
                name="Feature mart build dry-run",
                status=DailyPipelineStageStatus.READY,
                owner_role="Data Science Owner",
                process_key="feature_build_process",
                task_id="task-feature-build-001",
                details=(
                    f"feature_version={feature_plan.feature_version}; "
                    f"dependencies={feature_plan.dependency_count}; status={feature_status.value}"
                ),
            )
        )
    else:
        stages.append(
            DailyPipelineStage(
                stage_key="feature_build",
                name="Feature mart build dry-run",
                status=DailyPipelineStageStatus.SKIPPED,
                owner_role="Data Science Owner",
                process_key="feature_build_process",
                task_id="task-feature-build-001",
                details="Skipped until clean publication is ready.",
            )
        )

    final_status = "ready_for_feature_build" if all(
        stage.status in {DailyPipelineStageStatus.PASSED, DailyPipelineStageStatus.READY} for stage in stages
    ) else "blocked"
    run_id = f"daily-pipeline-gate-{request.business_date.isoformat()}"
    event = record_audit_event_if_enabled(
        AuditEventCreate(
            event_type="daily_pipeline_gate_run",
            actor=request.actor,
            actor_role=request.actor_role,
            object_type="daily_pipeline",
            object_id=run_id,
            action="run_daily_pipeline_gate",
            reason=f"status={final_status}",
            correlation_id=run_id,
            payload={
                "business_date": request.business_date.isoformat(),
                "status": final_status,
                "stages": [stage.model_dump(mode="json") for stage in stages],
            },
        )
    )
    return DailyPipelineGateResponse(
        run_id=run_id,
        business_date=request.business_date,
        status=final_status,
        stages=tuple(stages),
        audit_recorded=event is not None,
    )


@router.post("/run")
def run_daily_pipeline_gate_endpoint(request: DailyPipelineGateRequest) -> dict[str, object]:
    response = run_daily_pipeline_gate(request)
    return response.model_dump(mode="json")
