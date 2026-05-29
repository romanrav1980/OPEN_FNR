import json
from enum import StrEnum
from urllib.error import URLError
from urllib.request import Request, urlopen

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from .audit import AuditEventCreate, record_audit_event_if_enabled
from .config import settings


router = APIRouter(prefix="/supplier-collaboration", tags=["supplier-collaboration"])


class SupplierCollaborationStatus(StrEnum):
    FORECAST_SENT = "forecast_sent"
    CONFIRMED = "confirmed"
    RISK_REPORTED = "risk_reported"
    RESOLVED = "resolved"
    ESCALATED = "escalated"


class SupplierForecastShare(BaseModel):
    package_id: str
    supplier_id: str
    sku: str
    dc: str
    horizon_days: int
    forecast_qty: int
    order_forecast_qty: int
    status: SupplierCollaborationStatus
    cutoff_at: str
    export_channel: str
    idempotency_key: str


class SupplierPerformance(BaseModel):
    supplier_id: str
    fill_rate: float = Field(ge=0, le=1)
    on_time_rate: float = Field(ge=0, le=1)
    confirmation_rate: float = Field(ge=0, le=1)
    open_exceptions: int = Field(ge=0)


class SupplierConfirmationRequest(BaseModel):
    actor: str = Field(min_length=1)
    actor_role: str
    confirmed_qty: int = Field(ge=0)
    comment: str = Field(min_length=1)


class SupplierForecastShareSendRequest(BaseModel):
    actor: str = Field(min_length=1)
    actor_role: str = Field(default="Internal Supplier Coordinator", min_length=1)
    service_account: str = Field(min_length=1)


class SupplierForecastShareSendResponse(BaseModel):
    package: SupplierForecastShare
    response_code: str
    response_message: str
    audit_recorded: bool


FORECAST_SHARE = SupplierForecastShare(
    package_id="supplier-share-20260602-sup-fast",
    supplier_id="SUP_FAST",
    sku="SKU001",
    dc="DC001",
    horizon_days=30,
    forecast_qty=18_400,
    order_forecast_qty=12_000,
    status=SupplierCollaborationStatus.FORECAST_SENT,
    cutoff_at="2026-06-02T16:00:00+03:00",
    export_channel="local_fallback",
    idempotency_key="supplier-share-20260602-sup-fast:v1",
)


PERFORMANCE = SupplierPerformance(
    supplier_id="SUP_FAST",
    fill_rate=0.96,
    on_time_rate=0.91,
    confirmation_rate=0.88,
    open_exceptions=1,
)


def decide_supplier_risk(confirmed_qty: int, requested_qty: int) -> SupplierCollaborationStatus:
    if confirmed_qty >= requested_qty:
        return SupplierCollaborationStatus.CONFIRMED
    if confirmed_qty >= int(requested_qty * 0.8):
        return SupplierCollaborationStatus.RISK_REPORTED
    return SupplierCollaborationStatus.ESCALATED


def supplier_forecast_share_export_channel() -> str:
    return "http_api" if settings.supplier_forecast_share_url else "local_fallback"


def current_forecast_share() -> SupplierForecastShare:
    return FORECAST_SHARE.model_copy(update={"export_channel": supplier_forecast_share_export_channel()})


def supplier_forecast_share_payload(package: SupplierForecastShare) -> dict[str, object]:
    return package.model_dump(mode="json")


def send_supplier_forecast_share_to_target(package: SupplierForecastShare) -> tuple[str, str]:
    if not settings.supplier_forecast_share_url:
        return "202", "sent to local supplier fallback"
    request = Request(
        settings.supplier_forecast_share_url,
        data=json.dumps(supplier_forecast_share_payload(package), ensure_ascii=False).encode("utf-8"),
        headers={
            "Content-Type": "application/json; charset=utf-8",
            "Idempotency-Key": package.idempotency_key,
        },
        method="POST",
    )
    try:
        with urlopen(request, timeout=settings.publication_http_timeout_seconds) as response:
            response_body = response.read().decode("utf-8", errors="replace").strip()
            return str(response.status), response_body or "sent to supplier http target"
    except URLError as exc:
        raise HTTPException(status_code=503, detail=f"supplier forecast target unavailable: {exc}") from exc


@router.get("/forecast-share", response_model=tuple[SupplierForecastShare, ...])
def list_forecast_share() -> tuple[SupplierForecastShare, ...]:
    return (current_forecast_share(),)


@router.get("/performance", response_model=tuple[SupplierPerformance, ...])
def list_supplier_performance() -> tuple[SupplierPerformance, ...]:
    return (PERFORMANCE,)


@router.post("/forecast-share/{package_id}/send", response_model=SupplierForecastShareSendResponse)
def send_supplier_forecast_share(package_id: str, request: SupplierForecastShareSendRequest) -> SupplierForecastShareSendResponse:
    if package_id != FORECAST_SHARE.package_id:
        raise HTTPException(status_code=404, detail="Supplier forecast package not found")
    if request.service_account != "svc-open-fnr-supplier-share":
        raise HTTPException(status_code=403, detail="service account is not allowed to share supplier forecast")
    package = current_forecast_share()
    response_code, response_message = send_supplier_forecast_share_to_target(package)
    event = record_audit_event_if_enabled(
        AuditEventCreate(
            event_type="supplier_forecast_share_sent",
            actor=request.actor,
            actor_role=request.actor_role,
            object_type="supplier_forecast_share",
            object_id=package.package_id,
            action="send",
            reason=f"Sent supplier forecast through {package.export_channel}",
            correlation_id=package.idempotency_key,
            payload={
                "supplier_id": package.supplier_id,
                "sku": package.sku,
                "dc": package.dc,
                "idempotency_key": package.idempotency_key,
                "export_channel": package.export_channel,
            },
        )
    )
    return SupplierForecastShareSendResponse(
        package=package,
        response_code=response_code,
        response_message=response_message,
        audit_recorded=event is not None,
    )


@router.post("/forecast-share/{package_id}/confirm")
def confirm_supplier_forecast(package_id: str, request: SupplierConfirmationRequest) -> dict[str, object]:
    if package_id != FORECAST_SHARE.package_id:
        raise HTTPException(status_code=404, detail="Supplier forecast package not found")
    if request.actor_role not in {"Supplier User", "Internal Supplier Coordinator"}:
        raise HTTPException(status_code=403, detail="Role is not allowed to confirm supplier forecast")

    status = decide_supplier_risk(request.confirmed_qty, FORECAST_SHARE.order_forecast_qty)
    record_audit_event_if_enabled(
        AuditEventCreate(
            event_type="supplier_forecast_confirmed",
            actor=request.actor,
            actor_role=request.actor_role,
            object_type="supplier_forecast_share",
            object_id=package_id,
            action="confirm",
            reason=request.comment,
            correlation_id=FORECAST_SHARE.idempotency_key,
            payload={
                "supplier_id": FORECAST_SHARE.supplier_id,
                "requested_qty": FORECAST_SHARE.order_forecast_qty,
                "confirmed_qty": request.confirmed_qty,
                "status": status,
            },
        )
    )
    return {
        "package_id": package_id,
        "supplier_id": FORECAST_SHARE.supplier_id,
        "status": status,
        "confirmed_qty": request.confirmed_qty,
        "requested_qty": FORECAST_SHARE.order_forecast_qty,
        "supply_exception": status in {SupplierCollaborationStatus.RISK_REPORTED, SupplierCollaborationStatus.ESCALATED},
        "audit": {
            "actor": request.actor,
            "actor_role": request.actor_role,
            "comment": request.comment,
            "idempotency_key": FORECAST_SHARE.idempotency_key,
        },
    }
