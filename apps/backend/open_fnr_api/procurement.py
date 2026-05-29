import json
from datetime import datetime, timezone
from enum import StrEnum
from urllib.error import URLError
from urllib.request import Request, urlopen

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from .audit import AuditEventCreate, record_audit_event_if_enabled
from .config import settings


router = APIRouter(prefix="/procurement", tags=["procurement"])


class PurchaseProposalStatus(StrEnum):
    CALCULATED = "calculated"
    SUPPLIER_SELECTED = "supplier_selected"
    REVIEW_REQUIRED = "review_required"
    APPROVED = "approved"
    BLOCKED = "blocked"


class SupplierContract(BaseModel):
    supplier_id: str
    sku_id: str
    lead_time_days: int = Field(ge=0)
    fill_rate: float = Field(ge=0, le=1)
    unit_cost: float = Field(gt=0)
    min_order_qty: int = Field(gt=0)
    target_share: float = Field(ge=0, le=1)
    current_share: float = Field(ge=0, le=1)
    order_cutoff: str


class SupplierDecision(BaseModel):
    supplier_id: str
    score: float
    reason: str
    target_share_warning: bool


class PurchaseProposal(BaseModel):
    proposal_id: str
    sku_id: str
    dc_id: str
    qty: int = Field(gt=0)
    status: PurchaseProposalStatus
    selected_supplier_id: str
    decision: SupplierDecision
    calculated_at: datetime


class ProcurementActionRequest(BaseModel):
    actor: str = Field(min_length=1)
    actor_role: str
    reason: str = Field(min_length=1)


class PurchaseErpExportRequest(BaseModel):
    actor: str = Field(min_length=1)
    actor_role: str = Field(default="Procurement Planner", min_length=1)
    service_account: str = Field(min_length=1)


class PurchaseErpExportPreview(BaseModel):
    proposal_id: str
    target: str
    supplier_id: str
    qty: int = Field(gt=0)
    idempotency_key: str
    export_channel: str


class PurchaseErpExportResponse(BaseModel):
    export: PurchaseErpExportPreview
    response_code: str
    response_message: str
    audit_recorded: bool


CONTRACTS: tuple[SupplierContract, ...] = (
    SupplierContract(
        supplier_id="SUP_FAST",
        sku_id="SKU001",
        lead_time_days=2,
        fill_rate=0.96,
        unit_cost=101.5,
        min_order_qty=100,
        target_share=0.60,
        current_share=0.52,
        order_cutoff="16:00",
    ),
    SupplierContract(
        supplier_id="SUP_CHEAP",
        sku_id="SKU001",
        lead_time_days=5,
        fill_rate=0.90,
        unit_cost=96.0,
        min_order_qty=200,
        target_share=0.40,
        current_share=0.48,
        order_cutoff="12:00",
    ),
)


def supplier_score(contract: SupplierContract) -> float:
    lead_time_score = max(0, 1 - contract.lead_time_days / 10)
    cost_score = max(0, 1 - contract.unit_cost / 150)
    share_penalty = max(0, contract.current_share - contract.target_share)
    return round(contract.fill_rate * 0.5 + lead_time_score * 0.25 + cost_score * 0.2 - share_penalty * 0.2, 4)


def select_supplier(contracts: tuple[SupplierContract, ...]) -> SupplierDecision:
    scored = sorted(((supplier_score(contract), contract) for contract in contracts), key=lambda item: item[0], reverse=True)
    score, contract = scored[0]
    warning = contract.current_share > contract.target_share
    reason = "best fill-rate and lead-time score within target share" if not warning else "best score but above target share"
    return SupplierDecision(supplier_id=contract.supplier_id, score=score, reason=reason, target_share_warning=warning)


def build_purchase_proposal() -> PurchaseProposal:
    decision = select_supplier(CONTRACTS)
    status = PurchaseProposalStatus.SUPPLIER_SELECTED if not decision.target_share_warning else PurchaseProposalStatus.REVIEW_REQUIRED
    return PurchaseProposal(
        proposal_id="purchase-proposal-20260528-001",
        sku_id="SKU001",
        dc_id="DC001",
        qty=1200,
        status=status,
        selected_supplier_id=decision.supplier_id,
        decision=decision,
        calculated_at=datetime(2026, 5, 28, 23, 0, tzinfo=timezone.utc),
    )


def purchase_erp_export_channel() -> str:
    return "http_api" if settings.erp_export_url else "local_fallback"


def build_purchase_erp_export(proposal: PurchaseProposal) -> PurchaseErpExportPreview:
    return PurchaseErpExportPreview(
        proposal_id=proposal.proposal_id,
        target="ERP supplier purchase",
        supplier_id=proposal.selected_supplier_id,
        qty=proposal.qty,
        idempotency_key=f"{proposal.proposal_id}:{proposal.selected_supplier_id}:v1",
        export_channel=purchase_erp_export_channel(),
    )


def send_purchase_erp_export_to_target(export: PurchaseErpExportPreview) -> tuple[str, str]:
    if not settings.erp_export_url:
        return "202", "sent to local ERP purchase fallback"
    request = Request(
        settings.erp_export_url,
        data=json.dumps(export.model_dump(mode="json"), ensure_ascii=False).encode("utf-8"),
        headers={
            "Content-Type": "application/json; charset=utf-8",
            "Idempotency-Key": export.idempotency_key,
        },
        method="POST",
    )
    try:
        with urlopen(request, timeout=settings.publication_http_timeout_seconds) as response:
            response_body = response.read().decode("utf-8", errors="replace").strip()
            return str(response.status), response_body or "sent to ERP purchase target"
    except URLError as exc:
        raise HTTPException(status_code=503, detail=f"ERP purchase target unavailable: {exc}") from exc


@router.get("/contracts")
def list_supplier_contracts() -> dict[str, object]:
    return {"items": [item.model_dump(mode="json") for item in CONTRACTS], "total": len(CONTRACTS)}


@router.get("/proposals")
def list_purchase_proposals() -> dict[str, object]:
    proposal = build_purchase_proposal()
    return {"items": [proposal.model_dump(mode="json")], "total": 1}


@router.post("/proposals/{proposal_id}/approve")
def approve_purchase_proposal(proposal_id: str, payload: ProcurementActionRequest) -> dict[str, object]:
    proposal = build_purchase_proposal()
    if proposal.proposal_id != proposal_id:
        raise HTTPException(status_code=404, detail="purchase proposal not found")
    if payload.actor_role not in {"Supply Chain Manager", "Procurement Planner"}:
        raise HTTPException(status_code=403, detail="procurement role required")
    approved = proposal.model_copy(update={"status": PurchaseProposalStatus.APPROVED})
    return {"proposal": approved.model_dump(mode="json"), "audit_message": f"{payload.actor} approved supplier {proposal.selected_supplier_id}: {payload.reason}"}


@router.get("/proposals/{proposal_id}/erp-export")
def get_purchase_erp_export(proposal_id: str) -> dict[str, object]:
    proposal = build_purchase_proposal()
    if proposal.proposal_id != proposal_id:
        raise HTTPException(status_code=404, detail="purchase proposal not found")
    return build_purchase_erp_export(proposal).model_dump(mode="json")


@router.post("/proposals/{proposal_id}/erp-export/send", response_model=PurchaseErpExportResponse)
def send_purchase_erp_export(proposal_id: str, payload: PurchaseErpExportRequest) -> PurchaseErpExportResponse:
    proposal = build_purchase_proposal()
    if proposal.proposal_id != proposal_id:
        raise HTTPException(status_code=404, detail="purchase proposal not found")
    if payload.actor_role not in {"Supply Chain Manager", "Procurement Planner"}:
        raise HTTPException(status_code=403, detail="procurement role required")
    if payload.service_account != "svc-open-fnr-procurement-export":
        raise HTTPException(status_code=403, detail="service account is not allowed to export purchase proposal")
    export = build_purchase_erp_export(proposal)
    response_code, response_message = send_purchase_erp_export_to_target(export)
    event = record_audit_event_if_enabled(
        AuditEventCreate(
            event_type="purchase_erp_export_sent",
            actor=payload.actor,
            actor_role=payload.actor_role,
            object_type="purchase_proposal",
            object_id=proposal.proposal_id,
            action="send",
            reason=f"Sent purchase proposal through {export.export_channel}",
            correlation_id=export.idempotency_key,
            payload={
                "supplier_id": export.supplier_id,
                "qty": export.qty,
                "target": export.target,
                "export_channel": export.export_channel,
            },
        )
    )
    return PurchaseErpExportResponse(
        export=export,
        response_code=response_code,
        response_message=response_message,
        audit_recorded=event is not None,
    )
