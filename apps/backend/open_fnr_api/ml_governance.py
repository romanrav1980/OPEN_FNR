from datetime import datetime, timezone
from enum import StrEnum

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field


router = APIRouter(prefix="/ml-governance", tags=["ml-governance"])


class ModelReleaseStatus(StrEnum):
    CANDIDATE = "candidate"
    SHADOW = "shadow"
    APPROVED = "approved"
    RELEASED = "released"
    ROLLED_BACK = "rolled_back"


class DriftSeverity(StrEnum):
    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class ModelCandidate(BaseModel):
    model_id: str
    version: str
    algorithm: str
    training_snapshot_id: str
    wape: float = Field(ge=0)
    bias: float
    baseline_wape: float = Field(ge=0)
    shadow_wape: float = Field(ge=0)
    drift_severity: DriftSeverity
    status: ModelReleaseStatus


class ModelReleaseRequest(BaseModel):
    actor: str = Field(min_length=1)
    actor_role: str
    reason: str = Field(min_length=1)


class ModelAuditEvent(BaseModel):
    event_id: str
    model_id: str
    actor: str
    event_type: str
    message: str
    created_at: datetime


MODEL_CANDIDATES: tuple[ModelCandidate, ...] = (
    ModelCandidate(
        model_id="regular-demand-lgbm-v2",
        version="2026.05.28",
        algorithm="LightGBM",
        training_snapshot_id="train-snapshot-20260528-001",
        wape=14.9,
        bias=-0.4,
        baseline_wape=18.4,
        shadow_wape=15.2,
        drift_severity=DriftSeverity.LOW,
        status=ModelReleaseStatus.SHADOW,
    ),
)


def model_release_gate(candidate: ModelCandidate) -> bool:
    improves_baseline = candidate.wape < candidate.baseline_wape
    bias_ok = abs(candidate.bias) <= 2.0
    drift_ok = candidate.drift_severity in {DriftSeverity.NONE, DriftSeverity.LOW}
    shadow_ok = candidate.shadow_wape <= candidate.baseline_wape
    return improves_baseline and bias_ok and drift_ok and shadow_ok


def transition_model(candidate: ModelCandidate, action: str, payload: ModelReleaseRequest) -> ModelCandidate:
    if action in {"approve", "release"} and payload.actor_role != "Forecast Owner":
        raise HTTPException(status_code=403, detail="Forecast Owner role required")
    if action == "rollback" and payload.actor_role not in {"Forecast Owner", "Data Scientist"}:
        raise HTTPException(status_code=403, detail="Forecast Owner or Data Scientist role required")
    if action in {"approve", "release"} and not model_release_gate(candidate):
        raise HTTPException(status_code=409, detail="model release gate failed")
    status_by_action = {
        "approve": ModelReleaseStatus.APPROVED,
        "release": ModelReleaseStatus.RELEASED,
        "rollback": ModelReleaseStatus.ROLLED_BACK,
    }
    if action not in status_by_action:
        raise HTTPException(status_code=400, detail="unsupported model action")
    return candidate.model_copy(update={"status": status_by_action[action]})


@router.get("/candidates")
def list_model_candidates() -> dict[str, object]:
    return {"items": [item.model_dump(mode="json") for item in MODEL_CANDIDATES], "total": len(MODEL_CANDIDATES)}


@router.post("/candidates/{model_id}/{action}")
def act_on_model(model_id: str, action: str, payload: ModelReleaseRequest) -> dict[str, object]:
    candidate = next((item for item in MODEL_CANDIDATES if item.model_id == model_id), None)
    if candidate is None:
        raise HTTPException(status_code=404, detail="model candidate not found")
    updated = transition_model(candidate, action, payload)
    audit = ModelAuditEvent(
        event_id=f"model-audit-{model_id}-{action}",
        model_id=model_id,
        actor=payload.actor,
        event_type=f"model_{action}",
        message=payload.reason,
        created_at=datetime(2026, 5, 28, 18, 0, tzinfo=timezone.utc),
    )
    return {"model": updated.model_dump(mode="json"), "audit_event": audit.model_dump(mode="json")}


@router.get("/candidates/{model_id}/gate")
def get_model_gate(model_id: str) -> dict[str, object]:
    candidate = next((item for item in MODEL_CANDIDATES if item.model_id == model_id), None)
    if candidate is None:
        raise HTTPException(status_code=404, detail="model candidate not found")
    return {"model_id": model_id, "release_allowed": model_release_gate(candidate)}
