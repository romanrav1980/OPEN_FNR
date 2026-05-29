import json
from datetime import datetime, timezone
from enum import StrEnum
from urllib.error import URLError
from urllib.request import Request, urlopen

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from .audit import AuditEventCreate, record_audit_event_if_enabled
from .config import settings
from .repositories import OperationalDecisionRecord, operational_decision_repository


router = APIRouter(prefix="/publication", tags=["publication"])


class PublicationTarget(StrEnum):
    ERP = "erp"
    WMS = "wms"
    DWH = "dwh"
    BI = "bi"
    AUTO_ORDER = "auto_order"


class PublicationObjectType(StrEnum):
    FORECAST = "forecast"
    FINAL_ORDER = "final_order"


class ExportStatus(StrEnum):
    PREPARED = "prepared"
    SENT = "sent"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    FAILED = "failed"
    SUPERSEDED = "superseded"


class PublicationItem(BaseModel):
    object_type: PublicationObjectType
    object_id: str
    payload_version: str
    approved: bool


class PublicationPackage(BaseModel):
    package_id: str
    target: PublicationTarget
    status: ExportStatus
    idempotency_key: str
    items: list[PublicationItem] = Field(min_length=1)
    prepared_by: str
    prepared_at: datetime
    sent_at: datetime | None = None
    response_code: str | None = None
    response_message: str | None = None
    retry_count: int = Field(ge=0)
    linked_exception_id: str | None = None


class ExportRequest(BaseModel):
    actor: str = Field(min_length=1)
    service_account: str = Field(min_length=1)
    idempotency_key: str = Field(min_length=1)


class ExportResponse(BaseModel):
    package: PublicationPackage
    duplicate: bool


class TargetExportResult(BaseModel):
    response_code: str = Field(min_length=1, max_length=64)
    response_message: str = Field(min_length=1, max_length=512)


class ControlledExportGate(BaseModel):
    gate_id: str
    scope_id: str
    allowed_targets: tuple[PublicationTarget, ...]
    approved_package_ids: tuple[str, ...]
    stop_switch_active: bool
    idempotency_policy: str
    reconciliation_required: bool
    owner_role: str
    status: str


class ControlledExportReconciliation(BaseModel):
    reconciliation_id: str
    scope_id: str
    package_id: str
    target: PublicationTarget
    idempotency_key: str
    source_status: str
    target_status: str
    duplicate_detected: bool
    ready_to_resume: bool


class StopSwitch(BaseModel):
    switch_id: str
    active: bool
    reason: str
    owner_role: str
    blocks_targets: tuple[PublicationTarget, ...]


PUBLICATION_PACKAGES: tuple[PublicationPackage, ...] = (
    PublicationPackage(
        package_id="pub-wms-orders-20260528-001",
        target=PublicationTarget.WMS,
        status=ExportStatus.PREPARED,
        idempotency_key="wms:orders:20260528:001",
        items=[
            PublicationItem(
                object_type=PublicationObjectType.FINAL_ORDER,
                object_id="final-order-20260528-s001-sku002",
                payload_version="order-payload-v1",
                approved=True,
            )
        ],
        prepared_by="integration.owner@example.org",
        prepared_at=datetime(2026, 5, 28, 6, 30, tzinfo=timezone.utc),
        retry_count=0,
    ),
    PublicationPackage(
        package_id="pub-dwh-forecast-20260528-001",
        target=PublicationTarget.DWH,
        status=ExportStatus.ACCEPTED,
        idempotency_key="dwh:forecast:20260528:001",
        items=[
            PublicationItem(
                object_type=PublicationObjectType.FORECAST,
                object_id="regular-baseline-20260528-001",
                payload_version="forecast-payload-v1",
                approved=True,
            )
        ],
        prepared_by="integration.owner@example.org",
        prepared_at=datetime(2026, 5, 28, 5, 30, tzinfo=timezone.utc),
        sent_at=datetime(2026, 5, 28, 5, 40, tzinfo=timezone.utc),
        response_code="200",
        response_message="accepted",
        retry_count=0,
    ),
    PublicationPackage(
        package_id="pub-erp-orders-20260528-001",
        target=PublicationTarget.ERP,
        status=ExportStatus.FAILED,
        idempotency_key="erp:orders:20260528:001",
        items=[
            PublicationItem(
                object_type=PublicationObjectType.FINAL_ORDER,
                object_id="final-order-20260528-s001-sku003",
                payload_version="order-payload-v1",
                approved=True,
            )
        ],
        prepared_by="integration.owner@example.org",
        prepared_at=datetime(2026, 5, 28, 6, 35, tzinfo=timezone.utc),
        sent_at=datetime(2026, 5, 28, 6, 40, tzinfo=timezone.utc),
        response_code="ERP_TIMEOUT",
        response_message="ERP mock timeout",
        retry_count=1,
        linked_exception_id="exc-export-20260528-001",
    ),
    PublicationPackage(
        package_id="pub-wms-orders-20260528-002",
        target=PublicationTarget.WMS,
        status=ExportStatus.REJECTED,
        idempotency_key="wms:orders:20260528:002",
        items=[
            PublicationItem(
                object_type=PublicationObjectType.FINAL_ORDER,
                object_id="final-order-20260528-s001-sku001",
                payload_version="order-payload-v1",
                approved=False,
            )
        ],
        prepared_by="integration.owner@example.org",
        prepared_at=datetime(2026, 5, 28, 6, 45, tzinfo=timezone.utc),
        response_code="NOT_APPROVED",
        response_message="final order must be approved before export",
        retry_count=0,
    ),
)

CONTROLLED_EXPORT_GATE = ControlledExportGate(
    gate_id="controlled-export-gate-pilot-north-fresh-001",
    scope_id="pilot-north-fresh-001",
    allowed_targets=(PublicationTarget.ERP, PublicationTarget.AUTO_ORDER),
    approved_package_ids=("pub-wms-orders-20260528-001",),
    stop_switch_active=False,
    idempotency_policy="same_business_key_same_idempotency_key_no_duplicate_target_send",
    reconciliation_required=True,
    owner_role="Integration Owner",
    status="ready_for_controlled_export",
)

CONTROLLED_EXPORT_RECONCILIATION: tuple[ControlledExportReconciliation, ...] = (
    ControlledExportReconciliation(
        reconciliation_id="recon-controlled-export-20260615-001",
        scope_id="pilot-north-fresh-001",
        package_id="pub-wms-orders-20260528-001",
        target=PublicationTarget.ERP,
        idempotency_key="pilot:controlled-export:20260615:001",
        source_status="sent",
        target_status="accepted",
        duplicate_detected=False,
        ready_to_resume=True,
    ),
)

CONTROLLED_EXPORT_STOP_SWITCH = StopSwitch(
    switch_id="publication-stop-switch-pilot",
    active=False,
    reason="controlled export window approved",
    owner_role="Incident Manager",
    blocks_targets=(PublicationTarget.ERP, PublicationTarget.AUTO_ORDER),
)


def all_items_approved(package: PublicationPackage) -> bool:
    return all(item.approved for item in package.items)


def find_duplicate_export(idempotency_key: str) -> PublicationPackage | None:
    return next((package for package in PUBLICATION_PACKAGES if package.idempotency_key == idempotency_key), None)


def export_url_for_target(target: PublicationTarget) -> str:
    return {
        PublicationTarget.ERP: settings.erp_export_url,
        PublicationTarget.WMS: settings.wms_export_url,
        PublicationTarget.DWH: settings.dwh_export_url,
        PublicationTarget.BI: settings.bi_export_url,
        PublicationTarget.AUTO_ORDER: settings.auto_order_export_url,
    }[target]


def export_payload(package: PublicationPackage, request: ExportRequest) -> dict[str, object]:
    return {
        "package_id": package.package_id,
        "target": package.target.value,
        "idempotency_key": request.idempotency_key,
        "actor": request.actor,
        "service_account": request.service_account,
        "items": [item.model_dump(mode="json") for item in package.items],
    }


def send_to_publication_target(package: PublicationPackage, request: ExportRequest, retry: bool = False) -> TargetExportResult:
    target_url = export_url_for_target(package.target)
    if not target_url:
        return TargetExportResult(
            response_code="202",
            response_message="retry sent to mock target" if retry else "sent to mock target",
        )

    http_request = Request(
        target_url,
        data=json.dumps(export_payload(package, request), ensure_ascii=False).encode("utf-8"),
        headers={
            "Content-Type": "application/json; charset=utf-8",
            "Idempotency-Key": request.idempotency_key,
            "X-Service-Account": request.service_account,
        },
        method="POST",
    )
    try:
        with urlopen(http_request, timeout=settings.publication_http_timeout_seconds) as response:
            response_body = response.read().decode("utf-8", errors="replace").strip()
            return TargetExportResult(
                response_code=str(response.status),
                response_message=response_body or "sent to http target",
            )
    except URLError as exc:
        raise HTTPException(status_code=503, detail=f"publication target unavailable: {exc}") from exc


def send_export(package: PublicationPackage, request: ExportRequest) -> ExportResponse:
    duplicate = find_duplicate_export(request.idempotency_key)
    if duplicate is not None and duplicate.package_id != package.package_id:
        return ExportResponse(package=duplicate, duplicate=True)
    if request.service_account != "svc-open-fnr-export":
        raise HTTPException(status_code=403, detail="service account is not allowed to export")
    if not all_items_approved(package):
        raise HTTPException(status_code=409, detail="cannot export package with unapproved items")
    target_result = send_to_publication_target(package, request)
    sent_package = package.model_copy(
        update={
            "status": ExportStatus.SENT,
            "sent_at": datetime(2026, 5, 28, 7, 0, tzinfo=timezone.utc),
            "response_code": target_result.response_code,
            "response_message": target_result.response_message,
        }
    )
    record_audit_event_if_enabled(
        AuditEventCreate(
            event_type="publication_export_sent",
            actor=request.actor,
            actor_role="Integration Service",
            object_type="publication_package",
            object_id=package.package_id,
            action="send",
            reason=f"Export sent to {package.target}",
            correlation_id=request.idempotency_key,
            payload={
                "target": package.target,
                "idempotency_key": request.idempotency_key,
                "item_count": len(package.items),
            },
        )
    )
    operational_decision_repository.upsert_decision(
        OperationalDecisionRecord(
            decision_id=f"publication-send-{package.package_id}",
            decision_type="publication_export",
            object_type="publication_package",
            object_id=package.package_id,
            status=sent_package.status.value,
            actor=request.actor,
            actor_role="Integration Service",
            idempotency_key=request.idempotency_key,
            correlation_id=request.idempotency_key,
            payload={
                "target": package.target.value,
                "response_code": target_result.response_code,
                "response_message": target_result.response_message,
                "item_count": len(package.items),
            },
            created_at=sent_package.sent_at or datetime.now(timezone.utc),
            updated_at=sent_package.sent_at or datetime.now(timezone.utc),
        )
    )
    return ExportResponse(package=sent_package, duplicate=False)


def retry_export(package: PublicationPackage, request: ExportRequest) -> ExportResponse:
    if request.service_account != "svc-open-fnr-export":
        raise HTTPException(status_code=403, detail="service account is not allowed to export")
    if package.status != ExportStatus.FAILED:
        raise HTTPException(status_code=409, detail="only failed package can be retried")
    target_result = send_to_publication_target(package, request, retry=True)
    retried_package = package.model_copy(
        update={
            "status": ExportStatus.SENT,
            "sent_at": datetime(2026, 5, 28, 7, 5, tzinfo=timezone.utc),
            "response_code": target_result.response_code,
            "response_message": target_result.response_message,
            "retry_count": package.retry_count + 1,
        }
    )
    record_audit_event_if_enabled(
        AuditEventCreate(
            event_type="publication_export_retry",
            actor=request.actor,
            actor_role="Integration Service",
            object_type="publication_package",
            object_id=package.package_id,
            action="retry",
            reason=f"Retry failed export to {package.target}",
            correlation_id=request.idempotency_key,
            payload={
                "target": package.target,
                "idempotency_key": request.idempotency_key,
                "retry_count": retried_package.retry_count,
            },
        )
    )
    operational_decision_repository.upsert_decision(
        OperationalDecisionRecord(
            decision_id=f"publication-retry-{package.package_id}",
            decision_type="publication_export_retry",
            object_type="publication_package",
            object_id=package.package_id,
            status=retried_package.status.value,
            actor=request.actor,
            actor_role="Integration Service",
            idempotency_key=request.idempotency_key,
            correlation_id=request.idempotency_key,
            payload={
                "target": package.target.value,
                "response_code": target_result.response_code,
                "response_message": target_result.response_message,
                "retry_count": retried_package.retry_count,
            },
            created_at=retried_package.sent_at or datetime.now(timezone.utc),
            updated_at=retried_package.sent_at or datetime.now(timezone.utc),
        )
    )
    return ExportResponse(package=retried_package, duplicate=False)


def controlled_export_allowed(package: PublicationPackage, gate: ControlledExportGate = CONTROLLED_EXPORT_GATE) -> bool:
    return (
        gate.status == "ready_for_controlled_export"
        and not gate.stop_switch_active
        and package.target in gate.allowed_targets
        and all_items_approved(package)
        and gate.reconciliation_required
    )


@router.get("/packages")
def list_publication_packages() -> dict[str, object]:
    return {"items": [item.model_dump(mode="json") for item in PUBLICATION_PACKAGES], "total": len(PUBLICATION_PACKAGES)}


@router.get("/packages/{package_id}")
def get_publication_package(package_id: str) -> dict[str, object]:
    for package in PUBLICATION_PACKAGES:
        if package.package_id == package_id:
            return package.model_dump(mode="json")
    raise HTTPException(status_code=404, detail="publication package not found")


@router.post("/packages/{package_id}/send")
def send_publication_package(package_id: str, request: ExportRequest) -> dict[str, object]:
    package = next((item for item in PUBLICATION_PACKAGES if item.package_id == package_id), None)
    if package is None:
        raise HTTPException(status_code=404, detail="publication package not found")
    return send_export(package, request).model_dump(mode="json")


@router.post("/packages/{package_id}/retry")
def retry_publication_package(package_id: str, request: ExportRequest) -> dict[str, object]:
    package = next((item for item in PUBLICATION_PACKAGES if item.package_id == package_id), None)
    if package is None:
        raise HTTPException(status_code=404, detail="publication package not found")
    return retry_export(package, request).model_dump(mode="json")


@router.get("/controlled-export/gate")
def get_controlled_export_gate() -> dict[str, object]:
    return CONTROLLED_EXPORT_GATE.model_dump(mode="json")


@router.get("/controlled-export/reconciliation")
def get_controlled_export_reconciliation() -> dict[str, object]:
    return {
        "items": [item.model_dump(mode="json") for item in CONTROLLED_EXPORT_RECONCILIATION],
        "total": len(CONTROLLED_EXPORT_RECONCILIATION),
        "all_ready_to_resume": all(item.ready_to_resume and not item.duplicate_detected for item in CONTROLLED_EXPORT_RECONCILIATION),
    }


@router.get("/controlled-export/stop-switch")
def get_controlled_export_stop_switch() -> dict[str, object]:
    return CONTROLLED_EXPORT_STOP_SWITCH.model_dump(mode="json")
