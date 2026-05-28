from enum import StrEnum

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field


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
    task = next((item for item in STORE_TASKS if item.task_id == task_id), None)
    if task is None:
        raise HTTPException(status_code=404, detail="Store task not found")
    if request.actor_role not in {"Store Operations", "Inventory Data Owner"}:
        raise HTTPException(status_code=403, detail="Role is not allowed to complete store task")
    if request.store_id != task.store_id:
        raise HTTPException(status_code=403, detail="Store scope mismatch")

    corrected = request.counted_qty != TRUE_INVENTORY.virtual_stock
    return {
        "task_id": task_id,
        "status": InventoryStatus.CORRECTED if corrected else InventoryStatus.CHECKED,
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
