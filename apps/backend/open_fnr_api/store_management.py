import json
from enum import StrEnum
from urllib.error import URLError
from urllib.request import Request, urlopen

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from .audit import AuditEventCreate, record_audit_event_if_enabled
from .config import settings


router = APIRouter(prefix="/store-management", tags=["store-management"])


class InventoryStatus(StrEnum):
    CALCULATED = "calculated"
    LOW_CONFIDENCE = "low_confidence"
    TASK_CREATED = "task_created"
    CHECKED = "checked"
    CORRECTED = "corrected"
    CLOSED = "closed"


class StoreTaskType(StrEnum):
    STOCK_CHECK = "stock_check"
    PROMO_DISPLAY_CONFIRMATION = "promo_display_confirmation"
    STOCK_OUT_FEEDBACK = "stock_out_feedback"


class TrueInventoryRecord(BaseModel):
    store_id: str
    sku: str
    system_stock: int = Field(ge=0)
    pos_movements: int = Field(ge=0)
    deliveries: int = Field(ge=0)
    corrections: int
    virtual_stock: int = Field(ge=0)
    confidence: float = Field(ge=0, le=1)
    status: InventoryStatus
    suggestion: str


class StoreTask(BaseModel):
    task_id: str
    store_id: str
    sku: str
    task_type: StoreTaskType
    priority: str
    status: InventoryStatus
    sla_due_at: str
    instruction: str


class StoreTaskCompletionRequest(BaseModel):
    actor: str = Field(min_length=1)
    actor_role: str
    store_id: str
    counted_qty: int = Field(ge=0)
    comment: str = Field(min_length=1)
    photo_reference: str | None = None


class StoreTaskDispatchRequest(BaseModel):
    actor: str = Field(min_length=1)
    actor_role: str = Field(default="Store Operations", min_length=1)
    service_account: str = Field(min_length=1)


class StoreTaskDispatchPreview(BaseModel):
    target: str
    task_id: str
    store_id: str
    task_type: StoreTaskType
    priority: str
    sla_due_at: str
    instruction: str
    idempotency_key: str
    export_channel: str


class StoreTaskDispatchResponse(BaseModel):
    dispatch: StoreTaskDispatchPreview
    response_code: str
    response_message: str
    audit_recorded: bool


def calculate_virtual_stock(system_stock: int, pos_movements: int, deliveries: int, corrections: int) -> int:
    return max(system_stock - pos_movements + deliveries + corrections, 0)


TRUE_INVENTORY = TrueInventoryRecord(
    store_id="S001",
    sku="SKU001",
    system_stock=120,
    pos_movements=72,
    deliveries=0,
    corrections=-8,
    virtual_stock=40,
    confidence=0.58,
    status=InventoryStatus.LOW_CONFIDENCE,
    suggestion="Create store stock check and correct stock if count differs.",
)


STORE_TASKS = (
    StoreTask(
        task_id="store-task-stock-s001-sku001",
        store_id="S001",
        sku="SKU001",
        task_type=StoreTaskType.STOCK_CHECK,
        priority="high",
        status=InventoryStatus.TASK_CREATED,
        sla_due_at="2026-06-02T12:00:00+03:00",
        instruction="Count shelf and backroom stock for SKU001.",
    ),
    StoreTask(
        task_id="store-task-display-s001-sku001",
        store_id="S001",
        sku="SKU001",
        task_type=StoreTaskType.PROMO_DISPLAY_CONFIRMATION,
        priority="medium",
        status=InventoryStatus.TASK_CREATED,
        sla_due_at="2026-06-02T10:00:00+03:00",
        instruction="Confirm promo display is installed and filled.",
    ),
)


def store_app_task_export_channel() -> str:
    return "http_api" if settings.store_app_task_export_url else "local_fallback"


def find_store_task(task_id: str) -> StoreTask:
    task = next((item for item in STORE_TASKS if item.task_id == task_id), None)
    if task is None:
        raise HTTPException(status_code=404, detail="Store task not found")
    return task


def build_store_task_dispatch(task: StoreTask) -> StoreTaskDispatchPreview:
    return StoreTaskDispatchPreview(
        target="Store App task",
        task_id=task.task_id,
        store_id=task.store_id,
        task_type=task.task_type,
        priority=task.priority,
        sla_due_at=task.sla_due_at,
        instruction=task.instruction,
        idempotency_key=f"{task.task_id}:store-app:v1",
        export_channel=store_app_task_export_channel(),
    )


def send_store_task_to_target(dispatch: StoreTaskDispatchPreview) -> tuple[str, str]:
    if not settings.store_app_task_export_url:
        return "202", "sent to local store app fallback"
    request = Request(
        settings.store_app_task_export_url,
        data=json.dumps(dispatch.model_dump(mode="json"), ensure_ascii=False).encode("utf-8"),
        headers={
            "Content-Type": "application/json; charset=utf-8",
            "Idempotency-Key": dispatch.idempotency_key,
        },
        method="POST",
    )
    try:
        with urlopen(request, timeout=settings.publication_http_timeout_seconds) as response:
            response_body = response.read().decode("utf-8", errors="replace").strip()
            return str(response.status), response_body or "sent to store app target"
    except URLError as exc:
        raise HTTPException(status_code=503, detail=f"store app target unavailable: {exc}") from exc


@router.get("/true-inventory", response_model=tuple[TrueInventoryRecord, ...])
def list_true_inventory(store_id: str = Query(default="S001")) -> tuple[TrueInventoryRecord, ...]:
    if store_id != TRUE_INVENTORY.store_id:
        return ()
    return (TRUE_INVENTORY,)


@router.get("/tasks", response_model=tuple[StoreTask, ...])
def list_store_tasks(store_id: str = Query(default="S001")) -> tuple[StoreTask, ...]:
    return tuple(task for task in STORE_TASKS if task.store_id == store_id)


@router.post("/tasks/{task_id}/complete")
def complete_store_task(task_id: str, request: StoreTaskCompletionRequest) -> dict[str, object]:
    task = find_store_task(task_id)
    if request.actor_role not in {"Store Operations", "Inventory Data Owner"}:
        raise HTTPException(status_code=403, detail="Role is not allowed to complete store task")
    if request.store_id != task.store_id:
        raise HTTPException(status_code=403, detail="Store scope mismatch")

    corrected = request.counted_qty != TRUE_INVENTORY.virtual_stock
    status = InventoryStatus.CORRECTED if corrected else InventoryStatus.CHECKED
    record_audit_event_if_enabled(
        AuditEventCreate(
            event_type="store_task_completed",
            actor=request.actor,
            actor_role=request.actor_role,
            object_type="store_task",
            object_id=task_id,
            action="complete",
            reason=request.comment,
            correlation_id=f"{task_id}:{request.store_id}",
            payload={
                "store_id": request.store_id,
                "sku": task.sku,
                "task_type": task.task_type,
                "counted_qty": request.counted_qty,
                "previous_virtual_stock": TRUE_INVENTORY.virtual_stock,
                "status": status,
            },
        )
    )
    return {
        "task_id": task_id,
        "status": status,
        "counted_qty": request.counted_qty,
        "previous_virtual_stock": TRUE_INVENTORY.virtual_stock,
        "quality_flag": "store_feedback_received",
        "audit": {
            "actor": request.actor,
            "actor_role": request.actor_role,
            "store_id": request.store_id,
            "comment": request.comment,
            "photo_reference": request.photo_reference,
        },
    }


@router.get("/tasks/{task_id}/dispatch")
def get_store_task_dispatch(task_id: str) -> dict[str, object]:
    task = find_store_task(task_id)
    return build_store_task_dispatch(task).model_dump(mode="json")


@router.post("/tasks/{task_id}/dispatch/send", response_model=StoreTaskDispatchResponse)
def send_store_task_dispatch(task_id: str, request: StoreTaskDispatchRequest) -> StoreTaskDispatchResponse:
    if request.actor_role not in {"Store Operations", "Inventory Data Owner"}:
        raise HTTPException(status_code=403, detail="Role is not allowed to dispatch store task")
    if request.service_account != "svc-open-fnr-store-app":
        raise HTTPException(status_code=403, detail="service account is not allowed to dispatch store task")
    task = find_store_task(task_id)
    dispatch = build_store_task_dispatch(task)
    response_code, response_message = send_store_task_to_target(dispatch)
    event = record_audit_event_if_enabled(
        AuditEventCreate(
            event_type="store_task_dispatched",
            actor=request.actor,
            actor_role=request.actor_role,
            object_type="store_task",
            object_id=task_id,
            action="dispatch",
            reason=f"Sent store task through {dispatch.export_channel}",
            correlation_id=dispatch.idempotency_key,
            payload={
                "store_id": dispatch.store_id,
                "task_type": dispatch.task_type,
                "priority": dispatch.priority,
                "export_channel": dispatch.export_channel,
            },
        )
    )
    return StoreTaskDispatchResponse(
        dispatch=dispatch,
        response_code=response_code,
        response_message=response_message,
        audit_recorded=event is not None,
    )
