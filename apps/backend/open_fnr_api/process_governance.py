from datetime import datetime, timezone
from enum import StrEnum

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field


router = APIRouter(prefix="/process-governance", tags=["process-governance"])


class ProcessChangeStatus(StrEnum):
    DRAFT = "draft"
    REVIEW = "review"
    APPROVED = "approved"
    DEPLOYED = "deployed"
    ROLLED_BACK = "rolled_back"


class ArtifactKind(StrEnum):
    BPMN = "bpmn"
    DMN = "dmn"
    CMMN = "cmmn"


class ProcessVersion(BaseModel):
    process_key: str
    artifact_kind: ArtifactKind
    version: int = Field(gt=0)
    status: ProcessChangeStatus
    checksum: str
    deployed_at: datetime | None


class ProcessChangeRequest(BaseModel):
    change_id: str
    process_key: str
    artifact_kind: ArtifactKind
    from_version: int = Field(gt=0)
    to_version: int = Field(gt=0)
    status: ProcessChangeStatus
    risk: str
    owner_role: str
    release_notes: str


class ProcessDeployment(BaseModel):
    deployment_id: str
    change_id: str
    status: ProcessChangeStatus
    approver: str
    migration_required: bool
    existing_instances_safe: bool
    deployed_at: datetime | None


class ProcessActionRequest(BaseModel):
    actor: str = Field(min_length=1)
    actor_role: str
    comment: str = Field(min_length=1)


VERSIONS: tuple[ProcessVersion, ...] = (
    ProcessVersion(
        process_key="bulk_auto_approval_decision",
        artifact_kind=ArtifactKind.DMN,
        version=1,
        status=ProcessChangeStatus.DEPLOYED,
        checksum="sha256:bulk-auto-v1",
        deployed_at=datetime(2026, 5, 28, 20, 0, tzinfo=timezone.utc),
    ),
    ProcessVersion(
        process_key="bulk_auto_approval_decision",
        artifact_kind=ArtifactKind.DMN,
        version=2,
        status=ProcessChangeStatus.REVIEW,
        checksum="sha256:bulk-auto-v2",
        deployed_at=None,
    ),
)

CHANGE_REQUESTS: tuple[ProcessChangeRequest, ...] = (
    ProcessChangeRequest(
        change_id="proc-change-20260528-001",
        process_key="bulk_auto_approval_decision",
        artifact_kind=ArtifactKind.DMN,
        from_version=1,
        to_version=2,
        status=ProcessChangeStatus.REVIEW,
        risk="medium",
        owner_role="BPM Owner",
        release_notes="Tighten runtime threshold and keep existing instances on v1 until migration is approved.",
    ),
)


def process_change_deployable(change: ProcessChangeRequest) -> bool:
    return change.status == ProcessChangeStatus.REVIEW and change.risk in {"low", "medium"} and change.to_version > change.from_version


@router.get("/versions")
def list_process_versions() -> dict[str, object]:
    return {"items": [item.model_dump(mode="json") for item in VERSIONS], "total": len(VERSIONS)}


@router.get("/changes")
def list_process_changes() -> dict[str, object]:
    return {"items": [item.model_dump(mode="json") for item in CHANGE_REQUESTS], "total": len(CHANGE_REQUESTS)}


@router.post("/changes/{change_id}/deploy")
def deploy_process_change(change_id: str, payload: ProcessActionRequest) -> dict[str, object]:
    change = next((item for item in CHANGE_REQUESTS if item.change_id == change_id), None)
    if change is None:
        raise HTTPException(status_code=404, detail="process change not found")
    if payload.actor_role != "Release Manager":
        raise HTTPException(status_code=403, detail="Release Manager role required")
    if not process_change_deployable(change):
        raise HTTPException(status_code=409, detail="process change is not deployable")
    deployment = ProcessDeployment(
        deployment_id="proc-deploy-20260528-001",
        change_id=change_id,
        status=ProcessChangeStatus.DEPLOYED,
        approver=payload.actor,
        migration_required=True,
        existing_instances_safe=True,
        deployed_at=datetime(2026, 5, 28, 20, 30, tzinfo=timezone.utc),
    )
    return deployment.model_dump(mode="json")


@router.post("/changes/{change_id}/rollback")
def rollback_process_change(change_id: str, payload: ProcessActionRequest) -> dict[str, object]:
    if payload.actor_role not in {"Release Manager", "Process Owner"}:
        raise HTTPException(status_code=403, detail="Release Manager or Process Owner role required")
    if not any(item.change_id == change_id for item in CHANGE_REQUESTS):
        raise HTTPException(status_code=404, detail="process change not found")
    deployment = ProcessDeployment(
        deployment_id="proc-rollback-20260528-001",
        change_id=change_id,
        status=ProcessChangeStatus.ROLLED_BACK,
        approver=payload.actor,
        migration_required=False,
        existing_instances_safe=True,
        deployed_at=datetime(2026, 5, 28, 20, 45, tzinfo=timezone.utc),
    )
    return deployment.model_dump(mode="json")
