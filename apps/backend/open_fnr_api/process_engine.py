from datetime import datetime, timezone
from enum import StrEnum

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field


router = APIRouter(prefix="/process", tags=["process-engine"])


class ProcessArtifactType(StrEnum):
    BPMN = "bpmn"
    DMN = "dmn"
    CMMN = "cmmn"


class ProcessDefinitionStatus(StrEnum):
    DEPLOYED = "deployed"
    DRAFT = "draft"


class TaskStatus(StrEnum):
    OPEN = "open"
    COMPLETED = "completed"
    ESCALATED = "escalated"


class AuditEventType(StrEnum):
    PROCESS_STARTED = "process_started"
    TASK_CREATED = "task_created"
    TASK_COMPLETED = "task_completed"
    COMMENT_ADDED = "comment_added"
    SLA_ESCALATED = "sla_escalated"
    APPROVAL_REQUESTED = "approval_requested"
    APPROVED = "approved"
    REJECTED = "rejected"
    REWORK_REQUESTED = "rework_requested"


class ProcessDefinition(BaseModel):
    key: str
    name: str
    artifact_type: ProcessArtifactType
    version: int = Field(ge=1)
    status: ProcessDefinitionStatus
    deployment_id: str
    source_path: str
    owner_role: str


class ProcessTask(BaseModel):
    task_id: str
    process_instance_id: str
    process_key: str
    name: str
    status: TaskStatus
    assigned_role: str
    candidate_roles: tuple[str, ...]
    available_actions: tuple[str, ...]
    sla_due_at: datetime
    created_at: datetime
    business_key: str


class AuditEvent(BaseModel):
    event_id: str
    process_instance_id: str
    task_id: str | None
    event_type: AuditEventType
    actor: str
    message: str
    created_at: datetime


class CompleteTaskRequest(BaseModel):
    action: str
    actor: str
    actor_role: str | None = None
    comment: str = Field(min_length=1)


class CompleteTaskResponse(BaseModel):
    task: ProcessTask
    audit_events: tuple[AuditEvent, ...]


PROCESS_DEFINITIONS: tuple[ProcessDefinition, ...] = (
    ProcessDefinition(
        key="model_release_process",
        name="Model release process",
        artifact_type=ProcessArtifactType.BPMN,
        version=1,
        status=ProcessDefinitionStatus.DEPLOYED,
        deployment_id="flowable-dev-deploy-20260528-019",
        source_path="processes/ml-governance/model_release_process.bpmn20.xml",
        owner_role="Forecast Owner",
    ),
    ProcessDefinition(
        key="model_release_gate_decision",
        name="Model release gate decision",
        artifact_type=ProcessArtifactType.DMN,
        version=1,
        status=ProcessDefinitionStatus.DEPLOYED,
        deployment_id="flowable-dev-deploy-20260528-019",
        source_path="processes/ml-governance/model_release_gate_decision.dmn.xml",
        owner_role="Forecast Owner",
    ),
    ProcessDefinition(
        key="model_drift_case",
        name="Model drift case",
        artifact_type=ProcessArtifactType.CMMN,
        version=1,
        status=ProcessDefinitionStatus.DEPLOYED,
        deployment_id="flowable-dev-deploy-20260528-019",
        source_path="processes/ml-governance/model_drift_case.cmmn.xml",
        owner_role="Data Scientist",
    ),
    ProcessDefinition(
        key="industrial_data_load_process",
        name="Industrial data load process",
        artifact_type=ProcessArtifactType.BPMN,
        version=1,
        status=ProcessDefinitionStatus.DEPLOYED,
        deployment_id="flowable-dev-deploy-20260528-018",
        source_path="processes/data-scale/industrial_data_load_process.bpmn20.xml",
        owner_role="Data Platform Owner",
    ),
    ProcessDefinition(
        key="industrial_dq_gate_decision",
        name="Industrial DQ gate decision",
        artifact_type=ProcessArtifactType.DMN,
        version=1,
        status=ProcessDefinitionStatus.DEPLOYED,
        deployment_id="flowable-dev-deploy-20260528-018",
        source_path="processes/data-scale/industrial_dq_gate_decision.dmn.xml",
        owner_role="Data Platform Owner",
    ),
    ProcessDefinition(
        key="large_scale_data_incident_case",
        name="Large-scale data incident case",
        artifact_type=ProcessArtifactType.CMMN,
        version=1,
        status=ProcessDefinitionStatus.DEPLOYED,
        deployment_id="flowable-dev-deploy-20260528-018",
        source_path="processes/data-scale/large_scale_data_incident_case.cmmn.xml",
        owner_role="Data Platform Owner",
    ),
    ProcessDefinition(
        key="pilot_operational_process",
        name="Pilot operational process",
        artifact_type=ProcessArtifactType.BPMN,
        version=1,
        status=ProcessDefinitionStatus.DEPLOYED,
        deployment_id="flowable-dev-deploy-20260528-017",
        source_path="processes/pilot/pilot_operational_process.bpmn20.xml",
        owner_role="Business Owner",
    ),
    ProcessDefinition(
        key="pilot_acceptance_decision",
        name="Pilot acceptance decision",
        artifact_type=ProcessArtifactType.DMN,
        version=1,
        status=ProcessDefinitionStatus.DEPLOYED,
        deployment_id="flowable-dev-deploy-20260528-017",
        source_path="processes/pilot/pilot_acceptance_decision.dmn.xml",
        owner_role="Business Owner",
    ),
    ProcessDefinition(
        key="pilot_exception_case",
        name="Pilot exception case",
        artifact_type=ProcessArtifactType.CMMN,
        version=1,
        status=ProcessDefinitionStatus.DEPLOYED,
        deployment_id="flowable-dev-deploy-20260528-017",
        source_path="processes/pilot/pilot_exception_case.cmmn.xml",
        owner_role="Product Owner",
    ),
    ProcessDefinition(
        key="stage_daily_cycle_process",
        name="Stage daily cycle process",
        artifact_type=ProcessArtifactType.BPMN,
        version=1,
        status=ProcessDefinitionStatus.DEPLOYED,
        deployment_id="flowable-dev-deploy-20260528-016",
        source_path="processes/stage/stage_daily_cycle_process.bpmn20.xml",
        owner_role="Release Manager",
    ),
    ProcessDefinition(
        key="stage_go_no_go_decision",
        name="Stage go/no-go decision",
        artifact_type=ProcessArtifactType.DMN,
        version=1,
        status=ProcessDefinitionStatus.DEPLOYED,
        deployment_id="flowable-dev-deploy-20260528-016",
        source_path="processes/stage/stage_go_no_go_decision.dmn.xml",
        owner_role="Business Owner",
    ),
    ProcessDefinition(
        key="stage_uat_case",
        name="Stage UAT case",
        artifact_type=ProcessArtifactType.CMMN,
        version=1,
        status=ProcessDefinitionStatus.DEPLOYED,
        deployment_id="flowable-dev-deploy-20260528-016",
        source_path="processes/stage/stage_uat_case.cmmn.xml",
        owner_role="Business Owner",
    ),
    ProcessDefinition(
        key="access_request_process",
        name="Access request process",
        artifact_type=ProcessArtifactType.BPMN,
        version=1,
        status=ProcessDefinitionStatus.DEPLOYED,
        deployment_id="flowable-dev-deploy-20260528-015",
        source_path="processes/security/access_request_process.bpmn20.xml",
        owner_role="Security Owner",
    ),
    ProcessDefinition(
        key="role_assignment_decision",
        name="Role assignment decision",
        artifact_type=ProcessArtifactType.DMN,
        version=1,
        status=ProcessDefinitionStatus.DEPLOYED,
        deployment_id="flowable-dev-deploy-20260528-015",
        source_path="processes/security/role_assignment_decision.dmn.xml",
        owner_role="Security Owner",
    ),
    ProcessDefinition(
        key="security_incident_case",
        name="Security incident case",
        artifact_type=ProcessArtifactType.CMMN,
        version=1,
        status=ProcessDefinitionStatus.DEPLOYED,
        deployment_id="flowable-dev-deploy-20260528-015",
        source_path="processes/security/security_incident_case.cmmn.xml",
        owner_role="Security Owner",
    ),
    ProcessDefinition(
        key="performance_test_run_process",
        name="Performance test run process",
        artifact_type=ProcessArtifactType.BPMN,
        version=1,
        status=ProcessDefinitionStatus.DEPLOYED,
        deployment_id="flowable-dev-deploy-20260528-014",
        source_path="processes/performance/performance_test_run_process.bpmn20.xml",
        owner_role="Performance Engineer",
    ),
    ProcessDefinition(
        key="performance_gate_decision",
        name="Performance gate decision",
        artifact_type=ProcessArtifactType.DMN,
        version=1,
        status=ProcessDefinitionStatus.DEPLOYED,
        deployment_id="flowable-dev-deploy-20260528-014",
        source_path="processes/performance/performance_gate_decision.dmn.xml",
        owner_role="Architect",
    ),
    ProcessDefinition(
        key="performance_regression_case",
        name="Performance regression case",
        artifact_type=ProcessArtifactType.CMMN,
        version=1,
        status=ProcessDefinitionStatus.DEPLOYED,
        deployment_id="flowable-dev-deploy-20260528-014",
        source_path="processes/performance/performance_regression_case.cmmn.xml",
        owner_role="Performance Engineer",
    ),
    ProcessDefinition(
        key="dc_replenishment_process",
        name="DC replenishment process",
        artifact_type=ProcessArtifactType.BPMN,
        version=1,
        status=ProcessDefinitionStatus.DEPLOYED,
        deployment_id="flowable-dev-deploy-20260528-013",
        source_path="processes/multi-echelon/dc_replenishment_process.bpmn20.xml",
        owner_role="Supply Chain Manager",
    ),
    ProcessDefinition(
        key="dc_allocation_priority_decision",
        name="DC allocation priority decision",
        artifact_type=ProcessArtifactType.DMN,
        version=1,
        status=ProcessDefinitionStatus.DEPLOYED,
        deployment_id="flowable-dev-deploy-20260528-013",
        source_path="processes/multi-echelon/dc_allocation_priority_decision.dmn.xml",
        owner_role="Supply Chain Manager",
    ),
    ProcessDefinition(
        key="dc_shortage_case",
        name="DC shortage case",
        artifact_type=ProcessArtifactType.CMMN,
        version=1,
        status=ProcessDefinitionStatus.DEPLOYED,
        deployment_id="flowable-dev-deploy-20260528-013",
        source_path="processes/multi-echelon/dc_shortage_case.cmmn.xml",
        owner_role="Supply Chain Manager",
    ),
    ProcessDefinition(
        key="sku_phase_in_process",
        name="SKU phase-in process",
        artifact_type=ProcessArtifactType.BPMN,
        version=1,
        status=ProcessDefinitionStatus.DEPLOYED,
        deployment_id="flowable-dev-deploy-20260528-012",
        source_path="processes/lifecycle/sku_phase_in_process.bpmn20.xml",
        owner_role="Category Manager",
    ),
    ProcessDefinition(
        key="sku_phase_out_process",
        name="SKU phase-out process",
        artifact_type=ProcessArtifactType.BPMN,
        version=1,
        status=ProcessDefinitionStatus.DEPLOYED,
        deployment_id="flowable-dev-deploy-20260528-012",
        source_path="processes/lifecycle/sku_phase_out_process.bpmn20.xml",
        owner_role="Category Manager",
    ),
    ProcessDefinition(
        key="lifecycle_order_allowed_decision",
        name="Lifecycle order allowed decision",
        artifact_type=ProcessArtifactType.DMN,
        version=1,
        status=ProcessDefinitionStatus.DEPLOYED,
        deployment_id="flowable-dev-deploy-20260528-012",
        source_path="processes/lifecycle/lifecycle_order_allowed_decision.dmn.xml",
        owner_role="Replenishment Planner",
    ),
    ProcessDefinition(
        key="clearance_risk_case",
        name="Clearance risk case",
        artifact_type=ProcessArtifactType.CMMN,
        version=1,
        status=ProcessDefinitionStatus.DEPLOYED,
        deployment_id="flowable-dev-deploy-20260528-012",
        source_path="processes/lifecycle/clearance_risk_case.cmmn.xml",
        owner_role="Category Manager",
    ),
    ProcessDefinition(
        key="fresh_order_review_process",
        name="Fresh order review process",
        artifact_type=ProcessArtifactType.BPMN,
        version=1,
        status=ProcessDefinitionStatus.DEPLOYED,
        deployment_id="flowable-dev-deploy-20260528-011",
        source_path="processes/fresh/fresh_order_review_process.bpmn20.xml",
        owner_role="Fresh Manager",
    ),
    ProcessDefinition(
        key="fresh_spoilage_risk_decision",
        name="Fresh spoilage risk decision",
        artifact_type=ProcessArtifactType.DMN,
        version=1,
        status=ProcessDefinitionStatus.DEPLOYED,
        deployment_id="flowable-dev-deploy-20260528-011",
        source_path="processes/fresh/fresh_spoilage_risk_decision.dmn.xml",
        owner_role="Fresh Manager",
    ),
    ProcessDefinition(
        key="high_spoilage_risk_case",
        name="High spoilage risk case",
        artifact_type=ProcessArtifactType.CMMN,
        version=1,
        status=ProcessDefinitionStatus.DEPLOYED,
        deployment_id="flowable-dev-deploy-20260528-011",
        source_path="processes/fresh/high_spoilage_risk_case.cmmn.xml",
        owner_role="Fresh Manager",
    ),
    ProcessDefinition(
        key="weekly_kpi_review_process",
        name="Weekly KPI review process",
        artifact_type=ProcessArtifactType.BPMN,
        version=1,
        status=ProcessDefinitionStatus.DEPLOYED,
        deployment_id="flowable-dev-deploy-20260528-010",
        source_path="processes/kpi/weekly_kpi_review_process.bpmn20.xml",
        owner_role="Process Owner",
    ),
    ProcessDefinition(
        key="kpi_alert_decision",
        name="KPI alert decision",
        artifact_type=ProcessArtifactType.DMN,
        version=1,
        status=ProcessDefinitionStatus.DEPLOYED,
        deployment_id="flowable-dev-deploy-20260528-010",
        source_path="processes/kpi/kpi_alert_decision.dmn.xml",
        owner_role="Data Scientist",
    ),
    ProcessDefinition(
        key="kpi_degradation_case",
        name="KPI degradation case",
        artifact_type=ProcessArtifactType.CMMN,
        version=1,
        status=ProcessDefinitionStatus.DEPLOYED,
        deployment_id="flowable-dev-deploy-20260528-010",
        source_path="processes/kpi/kpi_degradation_case.cmmn.xml",
        owner_role="Process Owner",
    ),
    ProcessDefinition(
        key="publication_process",
        name="Publication process",
        artifact_type=ProcessArtifactType.BPMN,
        version=1,
        status=ProcessDefinitionStatus.DEPLOYED,
        deployment_id="flowable-dev-deploy-20260528-009",
        source_path="processes/publication/publication_process.bpmn20.xml",
        owner_role="Integration Owner",
    ),
    ProcessDefinition(
        key="publication_eligibility_decision",
        name="Publication eligibility decision",
        artifact_type=ProcessArtifactType.DMN,
        version=1,
        status=ProcessDefinitionStatus.DEPLOYED,
        deployment_id="flowable-dev-deploy-20260528-009",
        source_path="processes/publication/publication_eligibility_decision.dmn.xml",
        owner_role="Integration Owner",
    ),
    ProcessDefinition(
        key="export_failure_case",
        name="Export failure case",
        artifact_type=ProcessArtifactType.CMMN,
        version=1,
        status=ProcessDefinitionStatus.DEPLOYED,
        deployment_id="flowable-dev-deploy-20260528-009",
        source_path="processes/publication/export_failure_case.cmmn.xml",
        owner_role="Integration Owner",
    ),
    ProcessDefinition(
        key="manual_adjustment_process",
        name="Manual adjustment process",
        artifact_type=ProcessArtifactType.BPMN,
        version=1,
        status=ProcessDefinitionStatus.DEPLOYED,
        deployment_id="flowable-dev-deploy-20260528-008",
        source_path="processes/adjustments/manual_adjustment_process.bpmn20.xml",
        owner_role="Forecast Planner",
    ),
    ProcessDefinition(
        key="adjustment_approval_required_decision",
        name="Adjustment approval required decision",
        artifact_type=ProcessArtifactType.DMN,
        version=1,
        status=ProcessDefinitionStatus.DEPLOYED,
        deployment_id="flowable-dev-deploy-20260528-008",
        source_path="processes/adjustments/adjustment_approval_required_decision.dmn.xml",
        owner_role="Forecast Planner",
    ),
    ProcessDefinition(
        key="adjustment_dispute_case",
        name="Adjustment dispute case",
        artifact_type=ProcessArtifactType.CMMN,
        version=1,
        status=ProcessDefinitionStatus.DEPLOYED,
        deployment_id="flowable-dev-deploy-20260528-008",
        source_path="processes/adjustments/adjustment_dispute_case.cmmn.xml",
        owner_role="Category Manager",
    ),
    ProcessDefinition(
        key="exception_escalation_process",
        name="Exception escalation process",
        artifact_type=ProcessArtifactType.BPMN,
        version=1,
        status=ProcessDefinitionStatus.DEPLOYED,
        deployment_id="flowable-dev-deploy-20260528-007",
        source_path="processes/exceptions/exception_escalation_process.bpmn20.xml",
        owner_role="Process Owner",
    ),
    ProcessDefinition(
        key="exception_severity_decision",
        name="Exception severity decision",
        artifact_type=ProcessArtifactType.DMN,
        version=1,
        status=ProcessDefinitionStatus.DEPLOYED,
        deployment_id="flowable-dev-deploy-20260528-007",
        source_path="processes/exceptions/exception_severity_decision.dmn.xml",
        owner_role="Process Owner",
    ),
    ProcessDefinition(
        key="exception_owner_routing",
        name="Exception owner routing",
        artifact_type=ProcessArtifactType.DMN,
        version=1,
        status=ProcessDefinitionStatus.DEPLOYED,
        deployment_id="flowable-dev-deploy-20260528-007",
        source_path="processes/exceptions/exception_owner_routing.dmn.xml",
        owner_role="Process Owner",
    ),
    ProcessDefinition(
        key="generic_exception_case",
        name="Generic exception case",
        artifact_type=ProcessArtifactType.CMMN,
        version=1,
        status=ProcessDefinitionStatus.DEPLOYED,
        deployment_id="flowable-dev-deploy-20260528-007",
        source_path="processes/exceptions/generic_exception_case.cmmn.xml",
        owner_role="Process Owner",
    ),
    ProcessDefinition(
        key="manual_review_required_decision",
        name="Manual review required decision",
        artifact_type=ProcessArtifactType.DMN,
        version=1,
        status=ProcessDefinitionStatus.DEPLOYED,
        deployment_id="flowable-dev-deploy-20260528-006",
        source_path="processes/replenishment/manual_review_required_decision.dmn.xml",
        owner_role="Replenishment Planner",
    ),
    ProcessDefinition(
        key="order_exception_case",
        name="Order exception case",
        artifact_type=ProcessArtifactType.CMMN,
        version=1,
        status=ProcessDefinitionStatus.DEPLOYED,
        deployment_id="flowable-dev-deploy-20260528-006",
        source_path="processes/replenishment/order_exception_case.cmmn.xml",
        owner_role="Supply Chain Manager",
    ),
    ProcessDefinition(
        key="order_proposal_generation_process",
        name="Order proposal generation",
        artifact_type=ProcessArtifactType.BPMN,
        version=1,
        status=ProcessDefinitionStatus.DEPLOYED,
        deployment_id="flowable-dev-deploy-20260528-005",
        source_path="processes/replenishment/order_proposal_generation_process.bpmn20.xml",
        owner_role="Replenishment Planner",
    ),
    ProcessDefinition(
        key="order_auto_approval_decision",
        name="Order auto approval decision",
        artifact_type=ProcessArtifactType.DMN,
        version=1,
        status=ProcessDefinitionStatus.DEPLOYED,
        deployment_id="flowable-dev-deploy-20260528-005",
        source_path="processes/replenishment/order_auto_approval_decision.dmn.xml",
        owner_role="Replenishment Planner",
    ),
    ProcessDefinition(
        key="order_constraint_decision",
        name="Order constraint decision",
        artifact_type=ProcessArtifactType.DMN,
        version=1,
        status=ProcessDefinitionStatus.DEPLOYED,
        deployment_id="flowable-dev-deploy-20260528-005",
        source_path="processes/replenishment/order_constraint_decision.dmn.xml",
        owner_role="Replenishment Planner",
    ),
    ProcessDefinition(
        key="supplier_constraint_case",
        name="Supplier constraint case",
        artifact_type=ProcessArtifactType.CMMN,
        version=1,
        status=ProcessDefinitionStatus.DEPLOYED,
        deployment_id="flowable-dev-deploy-20260528-005",
        source_path="processes/replenishment/supplier_constraint_case.cmmn.xml",
        owner_role="Replenishment Planner",
    ),
    ProcessDefinition(
        key="replenishment_calculation_process",
        name="Replenishment calculation",
        artifact_type=ProcessArtifactType.BPMN,
        version=1,
        status=ProcessDefinitionStatus.DEPLOYED,
        deployment_id="flowable-dev-deploy-20260528-004",
        source_path="processes/replenishment/replenishment_calculation_process.bpmn20.xml",
        owner_role="Replenishment Planner",
    ),
    ProcessDefinition(
        key="stock_projection_quality_decision",
        name="Stock projection quality decision",
        artifact_type=ProcessArtifactType.DMN,
        version=1,
        status=ProcessDefinitionStatus.DEPLOYED,
        deployment_id="flowable-dev-deploy-20260528-004",
        source_path="processes/replenishment/stock_projection_quality_decision.dmn.xml",
        owner_role="Replenishment Planner",
    ),
    ProcessDefinition(
        key="stock_projection_issue_case",
        name="Stock projection issue case",
        artifact_type=ProcessArtifactType.CMMN,
        version=1,
        status=ProcessDefinitionStatus.DEPLOYED,
        deployment_id="flowable-dev-deploy-20260528-004",
        source_path="processes/replenishment/stock_projection_issue_case.cmmn.xml",
        owner_role="Replenishment Planner",
    ),
    ProcessDefinition(
        key="promo_planning_process",
        name="Promo planning approval",
        artifact_type=ProcessArtifactType.BPMN,
        version=1,
        status=ProcessDefinitionStatus.DEPLOYED,
        deployment_id="flowable-dev-deploy-20260528-003",
        source_path="processes/promo/promo_planning_process.bpmn20.xml",
        owner_role="Promo Planner",
    ),
    ProcessDefinition(
        key="promo_risk_classification",
        name="Promo risk classification",
        artifact_type=ProcessArtifactType.DMN,
        version=1,
        status=ProcessDefinitionStatus.DEPLOYED,
        deployment_id="flowable-dev-deploy-20260528-003",
        source_path="processes/promo/promo_risk_classification.dmn.xml",
        owner_role="Category Manager",
    ),
    ProcessDefinition(
        key="promo_approval_route",
        name="Promo approval route",
        artifact_type=ProcessArtifactType.DMN,
        version=1,
        status=ProcessDefinitionStatus.DEPLOYED,
        deployment_id="flowable-dev-deploy-20260528-003",
        source_path="processes/promo/promo_approval_route.dmn.xml",
        owner_role="Supply Chain Manager",
    ),
    ProcessDefinition(
        key="promo_shortage_case",
        name="Promo shortage case",
        artifact_type=ProcessArtifactType.CMMN,
        version=1,
        status=ProcessDefinitionStatus.DEPLOYED,
        deployment_id="flowable-dev-deploy-20260528-003",
        source_path="processes/promo/promo_shortage_case.cmmn.xml",
        owner_role="Supply Chain Manager",
    ),
    ProcessDefinition(
        key="promo_draft_validation_process",
        name="Promo draft validation",
        artifact_type=ProcessArtifactType.BPMN,
        version=1,
        status=ProcessDefinitionStatus.DEPLOYED,
        deployment_id="flowable-dev-deploy-20260528-001",
        source_path="processes/promo/promo_draft_validation_process.bpmn20.xml",
        owner_role="Promo Planner",
    ),
    ProcessDefinition(
        key="forecast_review_process",
        name="Forecast review",
        artifact_type=ProcessArtifactType.BPMN,
        version=1,
        status=ProcessDefinitionStatus.DEPLOYED,
        deployment_id="flowable-dev-deploy-20260528-001",
        source_path="processes/forecast/forecast_review_process.bpmn20.xml",
        owner_role="Forecast Planner",
    ),
    ProcessDefinition(
        key="replenishment_approval_process",
        name="Replenishment approval",
        artifact_type=ProcessArtifactType.BPMN,
        version=1,
        status=ProcessDefinitionStatus.DRAFT,
        deployment_id="flowable-dev-deploy-20260528-002",
        source_path="processes/process-engine/replenishment_approval_process.bpmn20.xml",
        owner_role="Replenishment Planner",
    ),
    ProcessDefinition(
        key="task_visibility_decision",
        name="Task visibility decision",
        artifact_type=ProcessArtifactType.DMN,
        version=1,
        status=ProcessDefinitionStatus.DEPLOYED,
        deployment_id="flowable-dev-deploy-20260528-002",
        source_path="processes/process-engine/task_visibility_decision.dmn.xml",
        owner_role="Admin",
    ),
    ProcessDefinition(
        key="process_exception_case",
        name="Process exception case",
        artifact_type=ProcessArtifactType.CMMN,
        version=1,
        status=ProcessDefinitionStatus.DEPLOYED,
        deployment_id="flowable-dev-deploy-20260528-002",
        source_path="processes/process-engine/process_exception_case.cmmn.xml",
        owner_role="Admin",
    ),
)

TASKS: tuple[ProcessTask, ...] = (
    ProcessTask(
        task_id="task-stock-projection-001",
        process_instance_id="proc-stock-projection-20260528-001",
        process_key="replenishment_calculation_process",
        name="Review stock-out projection",
        status=TaskStatus.OPEN,
        assigned_role="Replenishment Planner",
        candidate_roles=("Replenishment Planner", "Supply Chain Manager"),
        available_actions=("acknowledge", "create_order_proposal", "comment", "escalate"),
        sla_due_at=datetime(2026, 5, 28, 14, 30, tzinfo=timezone.utc),
        created_at=datetime(2026, 5, 28, 13, 45, tzinfo=timezone.utc),
        business_key="projection-20260528-s001-sku001",
    ),
    ProcessTask(
        task_id="task-promo-approval-category-001",
        process_instance_id="proc-promo-approval-20260601-001",
        process_key="promo_planning_process",
        name="Approve promo commercial terms",
        status=TaskStatus.OPEN,
        assigned_role="Category Manager",
        candidate_roles=("Category Manager",),
        available_actions=("approve", "reject", "request_rework", "comment"),
        sla_due_at=datetime(2026, 5, 29, 9, 0, tzinfo=timezone.utc),
        created_at=datetime(2026, 5, 28, 12, 10, tzinfo=timezone.utc),
        business_key="promo-20260601-fresh-001",
    ),
    ProcessTask(
        task_id="task-promo-approval-supply-001",
        process_instance_id="proc-promo-approval-20260601-001",
        process_key="promo_planning_process",
        name="Approve promo supply readiness",
        status=TaskStatus.OPEN,
        assigned_role="Supply Chain Manager",
        candidate_roles=("Supply Chain Manager",),
        available_actions=("approve", "reject", "request_rework", "escalate", "comment"),
        sla_due_at=datetime(2026, 5, 28, 17, 0, tzinfo=timezone.utc),
        created_at=datetime(2026, 5, 28, 12, 20, tzinfo=timezone.utc),
        business_key="promo-20260601-fresh-001",
    ),
    ProcessTask(
        task_id="task-promo-001",
        process_instance_id="proc-promo-20260601-001",
        process_key="promo_draft_validation_process",
        name="Resolve promo data issue",
        status=TaskStatus.OPEN,
        assigned_role="Promo Planner",
        candidate_roles=("Promo Planner", "Category Manager"),
        available_actions=("complete", "comment", "escalate"),
        sla_due_at=datetime(2026, 5, 28, 12, 0, tzinfo=timezone.utc),
        created_at=datetime(2026, 5, 28, 9, 15, tzinfo=timezone.utc),
        business_key="promo-20260605-grocery-002",
    ),
    ProcessTask(
        task_id="task-forecast-001",
        process_instance_id="proc-forecast-20260528-001",
        process_key="forecast_review_process",
        name="Review forecast anomaly",
        status=TaskStatus.OPEN,
        assigned_role="Forecast Planner",
        candidate_roles=("Forecast Planner", "Forecast Owner"),
        available_actions=("accept", "adjust", "comment"),
        sla_due_at=datetime(2026, 5, 28, 15, 0, tzinfo=timezone.utc),
        created_at=datetime(2026, 5, 28, 10, 5, tzinfo=timezone.utc),
        business_key="regular-baseline-20260528-001",
    ),
    ProcessTask(
        task_id="task-replenishment-001",
        process_instance_id="proc-repl-20260528-001",
        process_key="replenishment_approval_process",
        name="Approve replenishment exception",
        status=TaskStatus.ESCALATED,
        assigned_role="Replenishment Planner",
        candidate_roles=("Replenishment Planner", "Supply Chain Manager"),
        available_actions=("approve", "reject", "comment"),
        sla_due_at=datetime(2026, 5, 28, 11, 30, tzinfo=timezone.utc),
        created_at=datetime(2026, 5, 28, 8, 45, tzinfo=timezone.utc),
        business_key="order-proposal-20260528-001",
    ),
)

AUDIT_EVENTS: tuple[AuditEvent, ...] = (
    AuditEvent(
        event_id="audit-promo-approval-001",
        process_instance_id="proc-promo-approval-20260601-001",
        task_id=None,
        event_type=AuditEventType.APPROVAL_REQUESTED,
        actor="Promo Planner",
        message="Requested category and supply approvals for promo-20260601-fresh-001.",
        created_at=datetime(2026, 5, 28, 12, 0, tzinfo=timezone.utc),
    ),
    AuditEvent(
        event_id="audit-promo-approval-002",
        process_instance_id="proc-promo-approval-20260601-001",
        task_id="task-promo-approval-category-001",
        event_type=AuditEventType.TASK_CREATED,
        actor="Flowable",
        message="Created Category Manager approval task.",
        created_at=datetime(2026, 5, 28, 12, 10, tzinfo=timezone.utc),
    ),
    AuditEvent(
        event_id="audit-promo-001",
        process_instance_id="proc-promo-20260601-001",
        task_id=None,
        event_type=AuditEventType.PROCESS_STARTED,
        actor="Flowable",
        message="Started promo draft validation for promo-20260605-grocery-002.",
        created_at=datetime(2026, 5, 28, 9, 10, tzinfo=timezone.utc),
    ),
    AuditEvent(
        event_id="audit-promo-002",
        process_instance_id="proc-promo-20260601-001",
        task_id="task-promo-001",
        event_type=AuditEventType.TASK_CREATED,
        actor="Flowable",
        message="Created task Resolve promo data issue for Promo Planner.",
        created_at=datetime(2026, 5, 28, 9, 15, tzinfo=timezone.utc),
    ),
    AuditEvent(
        event_id="audit-repl-001",
        process_instance_id="proc-repl-20260528-001",
        task_id="task-replenishment-001",
        event_type=AuditEventType.SLA_ESCALATED,
        actor="Flowable",
        message="Escalated replenishment exception after SLA breach.",
        created_at=datetime(2026, 5, 28, 11, 31, tzinfo=timezone.utc),
    ),
)


@router.get("/definitions")
def list_process_definitions() -> dict[str, tuple[ProcessDefinition, ...]]:
    return {"items": PROCESS_DEFINITIONS}


@router.post("/deployments")
def deploy_process_definitions() -> dict[str, object]:
    return {
        "deployment_id": "flowable-dev-deploy-20260528-002",
        "status": "accepted",
        "definitions": PROCESS_DEFINITIONS,
    }


@router.get("/tasks")
def list_tasks(role: str | None = Query(default=None)) -> dict[str, tuple[ProcessTask, ...]]:
    if role is None:
        return {"items": TASKS}

    visible_tasks = tuple(task for task in TASKS if role in task.candidate_roles or role == task.assigned_role)
    return {"items": visible_tasks}


@router.post("/tasks/{task_id}/complete")
def complete_task(task_id: str, payload: CompleteTaskRequest) -> CompleteTaskResponse:
    task = next((item for item in TASKS if item.task_id == task_id), None)
    if task is None:
        raise HTTPException(status_code=404, detail="process task not found")
    if payload.action not in task.available_actions:
        raise HTTPException(status_code=400, detail="action is not available for task")
    if payload.actor_role is not None and payload.actor_role not in task.candidate_roles and payload.actor_role != task.assigned_role:
        raise HTTPException(status_code=403, detail="actor role is not allowed to complete task")

    completed_task = task.model_copy(update={"status": TaskStatus.COMPLETED})
    now = datetime(2026, 5, 28, 12, 5, tzinfo=timezone.utc)
    return CompleteTaskResponse(
        task=completed_task,
        audit_events=(
            AuditEvent(
                event_id=f"audit-{task_id}-comment",
                process_instance_id=task.process_instance_id,
                task_id=task.task_id,
                event_type=AuditEventType.COMMENT_ADDED,
                actor=payload.actor,
                message=payload.comment,
                created_at=now,
            ),
            AuditEvent(
                event_id=f"audit-{task_id}-completed",
                process_instance_id=task.process_instance_id,
                task_id=task.task_id,
                event_type=AuditEventType.TASK_COMPLETED,
                actor=payload.actor,
                message=f"Task completed with action {payload.action}.",
                created_at=now,
            ),
        ),
    )


@router.get("/instances/{process_instance_id}/audit")
def get_process_audit(process_instance_id: str) -> dict[str, tuple[AuditEvent, ...]]:
    events = tuple(event for event in AUDIT_EVENTS if event.process_instance_id == process_instance_id)
    if not events:
        raise HTTPException(status_code=404, detail="process instance audit not found")
    return {"items": events}


@router.get("/audit")
def list_audit_events() -> dict[str, tuple[AuditEvent, ...]]:
    return {"items": AUDIT_EVENTS}
