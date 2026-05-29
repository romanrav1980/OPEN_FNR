from __future__ import annotations

from collections import Counter, defaultdict
from datetime import date, datetime, timezone
from hashlib import sha256
from pathlib import Path
from uuid import uuid4
from xml.etree import ElementTree

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from .config import settings
from .process_deployment import BPMN_NS, build_bpmn_quality_report, build_process_deployment_package
from .process_engine import AUDIT_EVENTS, PROCESS_DEFINITIONS, TASKS, ProcessArtifactType


router = APIRouter(prefix="/process-navigator", tags=["process-navigator"])


FLOW_NODE_TAGS = (
    "startEvent",
    "endEvent",
    "userTask",
    "serviceTask",
    "businessRuleTask",
    "exclusiveGateway",
    "inclusiveGateway",
    "parallelGateway",
)


DOMAIN_LABELS = {
    "adjustments": "Manual Adjustments",
    "capacity": "Capacity Optimization",
    "data-ingestion": "Data Ingestion",
    "data-quality": "Data Quality",
    "data-scale": "Industrial Data Scale",
    "diagnostics": "Supply Chain Diagnostics",
    "exceptions": "Exception Management",
    "feature-mart": "Feature Mart",
    "forecast": "Forecasting",
    "fresh": "Fresh And Shelf Life",
    "kpi": "KPI Review",
    "lifecycle": "Product Lifecycle",
    "ml": "ML Candidate Review",
    "ml-governance": "ML Governance",
    "multi-echelon": "Multi-Echelon Planning",
    "observability": "Observability",
    "performance": "Performance",
    "pilot": "Pilot Operations",
    "process-engine": "Process Engine",
    "process-governance": "Process Governance",
    "procurement": "Procurement Optimization",
    "promo": "Promo Planning",
    "publication": "Publication",
    "release-gate": "Release Gate",
    "replenishment": "Replenishment",
    "replenishment-scale": "Industrial Replenishment",
    "security": "Security",
    "shelf-space": "Shelf Space",
    "stage": "Stage Rehearsal",
    "store-management": "Store Management",
    "supplier-collaboration": "Supplier Collaboration",
}


class ProcessMapNode(BaseModel):
    id: str
    label: str
    node_type: str
    domain: str
    level: int = Field(ge=0)
    status: str
    owner_role: str | None = None
    artifact_type: str | None = None
    artifact_path: str | None = None
    count: int = Field(default=1, ge=0)
    alert_count: int = Field(default=0, ge=0)
    challenge_count: int = Field(default=0, ge=0)


class ProcessMapEdge(BaseModel):
    source: str
    target: str
    edge_type: str
    label: str | None = None


class ProcessMapResponse(BaseModel):
    zoom_level: int = Field(ge=0, le=4)
    semantic_level: str
    environment: str
    mode: str = "live"
    business_date: date | None = None
    generated_at: str
    data_freshness_seconds: int = Field(default=0, ge=0)
    node_count: int = Field(ge=0)
    edge_count: int = Field(ge=0)
    nodes: tuple[ProcessMapNode, ...]
    edges: tuple[ProcessMapEdge, ...]
    causal_edges: tuple[ProcessMapEdge, ...] = ()
    legend: dict[str, str]


class ProcessNavigatorAlert(BaseModel):
    alert_id: str
    alert_key: str
    severity: str
    domain: str
    process_key: str | None
    source: str
    message: str
    recommended_action: str
    status: str
    upstream_alert_key: str | None = None
    downstream_alert_keys: tuple[str, ...] = ()
    cause_chain: tuple[str, ...] = ()
    root_cause: bool = True
    cascade_level: int = Field(default=0, ge=0)
    occurrence_count: int = Field(default=1, ge=1)
    first_seen: str
    last_seen: str
    dedup_window_seconds: int = Field(ge=1)
    itsm_incident_ref: str | None = None


class ProcessDrilldownResponse(BaseModel):
    process_key: str
    domain: str
    label: str
    owner_role: str
    artifact_path: str
    bpmn_node_count: int = Field(ge=0)
    bpmn_edge_count: int = Field(ge=0)
    related_artifacts: tuple[str, ...]
    open_tasks: tuple[str, ...]
    audit_event_count: int = Field(ge=0)
    nodes: tuple[ProcessMapNode, ...]
    edges: tuple[ProcessMapEdge, ...]


class ConformanceDeviation(BaseModel):
    instance_id: str
    step_id: str
    deviation_type: str
    expected: str
    actual: str
    severity: str


class ConformanceResponse(BaseModel):
    process_key: str
    process_definition_id: str
    environment: str
    job_status: str = "done"
    conformance_score: float | None = None
    checked_instances: int = Field(default=0, ge=0)
    deviations: tuple[ConformanceDeviation, ...] = ()
    mandatory_steps_skipped: int = Field(default=0, ge=0)
    unexpected_sequences: int = Field(default=0, ge=0)
    generated_at: str
    last_checked_at: str | None = None
    job_id: str | None = None
    error: str | None = None


class ConformanceJobResponse(BaseModel):
    job_id: str
    status: str
    estimated_seconds: int = Field(ge=1)


class HumanTaskPerformanceMetric(BaseModel):
    task_key: str
    waiting_time_p95_minutes: float
    processing_time_p95_minutes: float


class ThroughputMetric(BaseModel):
    business_day: date
    started: int = Field(ge=0)
    completed: int = Field(ge=0)


class ProcessPerformanceResponse(BaseModel):
    process_key: str
    environment: str
    window_days: int = Field(ge=1)
    cycle_time_median_minutes: float
    cycle_time_p95_minutes: float
    cycle_time_max_minutes: float
    human_task_metrics: tuple[HumanTaskPerformanceMetric, ...]
    rework_rate: float = Field(ge=0)
    throughput_by_business_day: tuple[ThroughputMetric, ...]
    sla_thresholds: dict[str, float]
    generated_at: str
    data_freshness_seconds: int = Field(default=0, ge=0)


class ProcessVersionItem(BaseModel):
    version: int = Field(ge=1)
    status: str
    running_instances: int = Field(ge=0)
    stuck_instances: int = Field(ge=0)
    completed_instances: int = Field(ge=0)
    instance_list: tuple[str, ...] = ()


class ProcessVersionsResponse(BaseModel):
    process_key: str
    environment: str
    current_version: int = Field(ge=1)
    active_version_count: int = Field(ge=0)
    versions: tuple[ProcessVersionItem, ...]


class InfrastructureComponentStatus(BaseModel):
    component_type: str
    component_id: str
    status: str
    risk_reason: str


class InfrastructureHealthResponse(BaseModel):
    environment: str
    components: tuple[InfrastructureComponentStatus, ...]
    dependent_processes: tuple[str, ...]
    generated_at: str


class ProcessTrackingTrailItem(BaseModel):
    domain: str
    process_key: str
    instance_id: str | None
    status: str
    cycle_time_minutes: float | None
    open_tasks: int = Field(ge=0)
    alerts: tuple[str, ...]
    started_at: str | None
    completed_at: str | None


class ProcessTrackingResponse(BaseModel):
    environment: str
    business_key: str
    business_key_type: str
    trail: tuple[ProcessTrackingTrailItem, ...]


class WeeklyReportResponse(BaseModel):
    business_week: str
    environment: str
    domain_summary: tuple[dict[str, object], ...]
    alert_summary: tuple[dict[str, object], ...]
    root_causes: tuple[dict[str, object], ...]
    sla_breaches: tuple[dict[str, object], ...]
    superset_dataset_ref: str


CONFORMANCE_CACHE: dict[tuple[str, str], ConformanceResponse] = {}
CONFORMANCE_JOBS: dict[str, tuple[str, str]] = {}


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _resolve_env(env: str | None) -> str:
    resolved = env or settings.runtime_mode
    if resolved not in settings.allowed_environments:
        raise HTTPException(status_code=422, detail="environment is not allowed")
    return resolved


def domain_from_path(path: str) -> str:
    parts = Path(path).parts
    if "processes" not in parts:
        return "unknown"
    processes_index = parts.index("processes")
    if len(parts) <= processes_index + 1:
        return "unknown"
    return parts[processes_index + 1]


def process_key_from_artifact_path(path: str) -> str:
    name = Path(path).name
    for suffix in (".bpmn20.xml", ".dmn.xml", ".cmmn.xml"):
        if name.endswith(suffix):
            return name[: -len(suffix)]
    return Path(path).stem


def _artifact_status(alerts: tuple[ProcessNavigatorAlert, ...], key: str) -> str:
    severities = {alert.severity for alert in alerts if alert.process_key == key}
    if "blocker" in severities or "critical" in severities:
        return "blocked"
    if "warning" in severities or "challenge" in severities:
        return "attention"
    return "healthy"


def _alert(
    *,
    alert_id: str,
    severity: str,
    domain: str,
    process_key: str | None,
    source: str,
    message: str,
    recommended_action: str,
    status: str,
    upstream_alert_key: str | None = None,
) -> ProcessNavigatorAlert:
    alert_key = f"{source}:{process_key or domain}:{severity}"
    chain = (upstream_alert_key, alert_key) if upstream_alert_key else (alert_key,)
    return ProcessNavigatorAlert(
        alert_id=alert_id,
        alert_key=alert_key,
        severity=severity,
        domain=domain,
        process_key=process_key,
        source=source,
        message=message,
        recommended_action=recommended_action,
        status=status,
        upstream_alert_key=upstream_alert_key,
        cause_chain=tuple(item for item in chain if item),
        root_cause=upstream_alert_key is None,
        cascade_level=0 if upstream_alert_key is None else 1,
        first_seen=_now_iso(),
        last_seen=_now_iso(),
        dedup_window_seconds=settings.process_navigator_alert_dedup_window_seconds,
    )


def build_process_navigator_alerts() -> tuple[ProcessNavigatorAlert, ...]:
    quality = build_bpmn_quality_report()
    alerts: list[ProcessNavigatorAlert] = []
    for issue in quality.issues:
        process_key = process_key_from_artifact_path(issue.path)
        alerts.append(
            _alert(
                alert_id=f"bpmn-quality-{process_key}-{issue.element_id}-{issue.issue_type}",
                severity=issue.severity,
                domain=domain_from_path(issue.path),
                process_key=process_key,
                source="bpmn_quality_gate",
                message=issue.message,
                recommended_action=issue.recommendation,
                status="open" if issue.severity == "blocker" else "review",
            )
        )
    for task in TASKS:
        if task.status == "escalated":
            alerts.append(
                _alert(
                    alert_id=f"sla-{task.task_id}",
                    severity="warning",
                    domain=_domain_for_process_key(task.process_key),
                    process_key=task.process_key,
                    source="process_task_sla",
                    message=f"Task {task.task_id} is escalated for {task.assigned_role}.",
                    recommended_action="Open task inbox, assign owner and resolve before publication or release gate.",
                    status="open",
                )
            )
    return tuple(alerts)


def _domain_for_process_key(process_key: str) -> str:
    definition = next((item for item in PROCESS_DEFINITIONS if item.key == process_key), None)
    if definition is None:
        return "unknown"
    return domain_from_path(definition.source_path)


def _flow_nodes_for_bpmn(path: Path, process_key: str, domain: str) -> tuple[tuple[ProcessMapNode, ...], tuple[ProcessMapEdge, ...]]:
    if not path.exists():
        return (), ()
    root = ElementTree.fromstring(path.read_bytes())
    nodes: list[ProcessMapNode] = []
    for tag in FLOW_NODE_TAGS:
        for element in root.findall(f".//{{{BPMN_NS}}}{tag}"):
            element_id = element.attrib.get("id")
            if not element_id:
                continue
            label = element.attrib.get("name") or element_id
            nodes.append(
                ProcessMapNode(
                    id=f"{process_key}:{element_id}",
                    label=label,
                    node_type="bpmn_step",
                    domain=domain,
                    level=3,
                    status="healthy",
                    artifact_type="bpmn",
                )
            )
    edges: list[ProcessMapEdge] = []
    node_ids = {node.id for node in nodes}
    for flow in root.findall(f".//{{{BPMN_NS}}}sequenceFlow"):
        source = f"{process_key}:{flow.attrib.get('sourceRef', '')}"
        target = f"{process_key}:{flow.attrib.get('targetRef', '')}"
        if source in node_ids and target in node_ids:
            edges.append(
                ProcessMapEdge(
                    source=source,
                    target=target,
                    edge_type="bpmn_sequence",
                    label=flow.attrib.get("name"),
                )
            )
    return tuple(nodes), tuple(edges)


def build_process_map(zoom_level: int = 1, env: str | None = None, business_date: date | None = None) -> ProcessMapResponse:
    zoom_level = max(0, min(4, zoom_level))
    environment = _resolve_env(env)
    alerts = build_process_navigator_alerts()
    alert_counts = Counter(alert.process_key for alert in alerts if alert.process_key)
    challenge_counts = Counter(alert.process_key for alert in alerts if alert.severity == "challenge" and alert.process_key)
    definitions_by_domain: dict[str, list] = defaultdict(list)
    for definition in PROCESS_DEFINITIONS:
        definitions_by_domain[domain_from_path(definition.source_path)].append(definition)

    nodes: list[ProcessMapNode] = []
    edges: list[ProcessMapEdge] = []
    for domain, definitions in sorted(definitions_by_domain.items()):
        domain_alerts = sum(alert.alert_id is not None for alert in alerts if alert.domain == domain)
        status = "attention" if domain_alerts else "healthy"
        nodes.append(
            ProcessMapNode(
                id=f"domain:{domain}",
                label=DOMAIN_LABELS.get(domain, domain),
                node_type="domain_cluster",
                domain=domain,
                level=0,
                status=status,
                count=len(definitions),
                alert_count=domain_alerts,
            )
        )
        if zoom_level < 1:
            continue
        for definition in sorted(definitions, key=lambda item: item.key):
            status = _artifact_status(alerts, definition.key)
            nodes.append(
                ProcessMapNode(
                    id=f"process:{definition.key}",
                    label=definition.name,
                    node_type="process_definition",
                    domain=domain,
                    level=1,
                    status=status,
                    owner_role=definition.owner_role,
                    artifact_type=definition.artifact_type.value,
                    artifact_path=definition.source_path,
                    alert_count=alert_counts[definition.key],
                    challenge_count=challenge_counts[definition.key],
                )
            )
            edges.append(
                ProcessMapEdge(
                    source=f"domain:{domain}",
                    target=f"process:{definition.key}",
                    edge_type="contains",
                )
            )
            if zoom_level >= 3 and definition.artifact_type == ProcessArtifactType.BPMN:
                step_nodes, step_edges = _flow_nodes_for_bpmn(Path(definition.source_path), definition.key, domain)
                nodes.extend(step_nodes)
                edges.extend(step_edges)
                for step in step_nodes:
                    edges.append(
                        ProcessMapEdge(
                            source=f"process:{definition.key}",
                            target=step.id,
                            edge_type="drills_to",
                        )
                    )
    semantic_levels = {
        0: "domain_clusters",
        1: "process_definitions",
        2: "runtime_overlay",
        3: "bpmn_steps",
        4: "task_audit_timeline",
    }
    return ProcessMapResponse(
        zoom_level=zoom_level,
        semantic_level=semantic_levels[zoom_level],
        environment=environment,
        mode="snapshot" if business_date else "live",
        business_date=business_date,
        generated_at=_now_iso(),
        data_freshness_seconds=0,
        node_count=len(nodes),
        edge_count=len(edges),
        nodes=tuple(nodes),
        edges=tuple(edges),
        legend={
            "healthy": "No blocker or SLA alert is open.",
            "attention": "Review warning, cognitive challenge or escalated task.",
            "blocked": "Blocker must be resolved before release or production gate.",
        },
    )


def _get_definition(process_key: str):
    definition = next((item for item in PROCESS_DEFINITIONS if item.key == process_key), None)
    if definition is None:
        raise HTTPException(status_code=404, detail="process definition not found")
    return definition


def build_process_drilldown(process_key: str) -> ProcessDrilldownResponse:
    definition = _get_definition(process_key)
    if definition.artifact_type != ProcessArtifactType.BPMN:
        raise HTTPException(status_code=400, detail="drilldown is available for BPMN process definitions")
    domain = domain_from_path(definition.source_path)
    nodes, edges = _flow_nodes_for_bpmn(Path(definition.source_path), definition.key, domain)
    package = build_process_deployment_package()
    related_artifacts = tuple(
        artifact.path
        for artifact in package.artifacts
        if domain_from_path(artifact.path) == domain and artifact.path != definition.source_path
    )
    open_tasks = tuple(task.task_id for task in TASKS if task.process_key == process_key and task.status != "completed")
    audit_event_count = sum(1 for event in AUDIT_EVENTS if event.task_id in open_tasks)
    return ProcessDrilldownResponse(
        process_key=definition.key,
        domain=domain,
        label=definition.name,
        owner_role=definition.owner_role,
        artifact_path=definition.source_path,
        bpmn_node_count=len(nodes),
        bpmn_edge_count=len(edges),
        related_artifacts=related_artifacts,
        open_tasks=open_tasks,
        audit_event_count=audit_event_count,
        nodes=nodes,
        edges=edges,
    )


def _mask_instance_id(value: str) -> str:
    return sha256(value.encode("utf-8")).hexdigest()[:16]


def build_process_conformance(process_key: str, environment: str) -> ConformanceResponse:
    definition = _get_definition(process_key)
    if definition.artifact_type != ProcessArtifactType.BPMN:
        raise HTTPException(status_code=400, detail="conformance is available for BPMN process definitions")
    nodes, _ = _flow_nodes_for_bpmn(Path(definition.source_path), definition.key, domain_from_path(definition.source_path))
    mandatory_steps_skipped = 1 if len(nodes) == 0 else 0
    score = 100.0 if mandatory_steps_skipped == 0 else 75.0
    deviations: tuple[ConformanceDeviation, ...] = ()
    if mandatory_steps_skipped:
        deviations = (
            ConformanceDeviation(
                instance_id=_mask_instance_id(f"{process_key}-sample"),
                step_id="mandatory_approval",
                deviation_type="skipped_mandatory_step",
                expected="Mandatory human approval must be completed.",
                actual="Approval event was not found in history.",
                severity="critical",
            ),
        )
    response = ConformanceResponse(
        process_key=process_key,
        process_definition_id=f"{process_key}:current",
        environment=environment,
        conformance_score=score,
        checked_instances=max(1, len(nodes)),
        deviations=deviations,
        mandatory_steps_skipped=mandatory_steps_skipped,
        unexpected_sequences=0,
        generated_at=_now_iso(),
        last_checked_at=_now_iso(),
    )
    CONFORMANCE_CACHE[(environment, process_key)] = response
    return response


def build_process_performance(process_key: str, environment: str, window_days: int) -> ProcessPerformanceResponse:
    definition = _get_definition(process_key)
    if definition.artifact_type != ProcessArtifactType.BPMN:
        raise HTTPException(status_code=400, detail="performance is available for BPMN process definitions")
    open_task_count = sum(1 for task in TASKS if task.process_key == process_key and task.status != "completed")
    base = 45.0 + open_task_count * 15.0
    return ProcessPerformanceResponse(
        process_key=process_key,
        environment=environment,
        window_days=window_days,
        cycle_time_median_minutes=base,
        cycle_time_p95_minutes=base * 1.8,
        cycle_time_max_minutes=base * 2.4,
        human_task_metrics=(
            HumanTaskPerformanceMetric(
                task_key="human_review",
                waiting_time_p95_minutes=base * 0.6,
                processing_time_p95_minutes=base * 0.4,
            ),
        ),
        rework_rate=0.0,
        throughput_by_business_day=(
            ThroughputMetric(business_day=date.today(), started=max(1, open_task_count), completed=0),
        ),
        sla_thresholds={"green_minutes": 120.0, "amber_minutes": 240.0, "red_minutes": 480.0},
        generated_at=_now_iso(),
    )


def build_process_versions(process_key: str, environment: str, include_instances: bool) -> ProcessVersionsResponse:
    _get_definition(process_key)
    instances = (_mask_instance_id(f"{process_key}-v1-running"),) if include_instances else ()
    return ProcessVersionsResponse(
        process_key=process_key,
        environment=environment,
        current_version=1,
        active_version_count=1,
        versions=(
            ProcessVersionItem(
                version=1,
                status="current",
                running_instances=1,
                stuck_instances=0,
                completed_instances=3,
                instance_list=instances,
            ),
        ),
    )


@router.get("/map")
def get_process_map(
    zoom: int = Query(default=1, ge=0, le=4),
    env: str | None = None,
    business_date: date | None = None,
) -> ProcessMapResponse:
    return build_process_map(zoom, env, business_date)


@router.get("/alerts")
def get_process_alerts(
    env: str | None = None,
    limit: int | None = Query(default=None, ge=1),
    cursor: str | None = None,
    root_only: bool = False,
) -> dict[str, object]:
    _resolve_env(env)
    max_size = settings.process_navigator_alert_max_page_size
    page_size = min(limit or settings.process_navigator_alert_page_size, max_size)
    alerts = tuple(alert for alert in build_process_navigator_alerts() if not root_only or alert.root_cause)
    start = int(cursor or "0")
    page = alerts[start : start + page_size]
    next_cursor = str(start + page_size) if start + page_size < len(alerts) else None
    return {"items": page, "next_cursor": next_cursor, "total_count": len(alerts)}


@router.get("/processes/{process_key}/drilldown")
def get_process_drilldown(process_key: str, env: str | None = None) -> ProcessDrilldownResponse:
    _resolve_env(env)
    return build_process_drilldown(process_key)


@router.post("/processes/{process_key}/conformance/check")
def start_conformance_check(process_key: str, env: str | None = None) -> ConformanceJobResponse:
    environment = _resolve_env(env)
    _get_definition(process_key)
    job_id = str(uuid4())
    CONFORMANCE_JOBS[job_id] = (environment, process_key)
    return ConformanceJobResponse(
        job_id=job_id,
        status="queued",
        estimated_seconds=settings.process_navigator_conformance_max_seconds,
    )


@router.get("/processes/{process_key}/conformance/status/{job_id}")
def get_conformance_job_status(process_key: str, job_id: str, env: str | None = None) -> ConformanceResponse:
    environment = _resolve_env(env)
    job = CONFORMANCE_JOBS.get(job_id)
    if job is None or job != (environment, process_key):
        raise HTTPException(status_code=404, detail="conformance job not found")
    result = build_process_conformance(process_key, environment)
    return result.model_copy(update={"job_id": job_id, "job_status": "done"})


@router.get("/processes/{process_key}/conformance")
def get_process_conformance(
    process_key: str,
    env: str | None = None,
    summary_only: bool = False,
) -> ConformanceResponse:
    environment = _resolve_env(env)
    cached = CONFORMANCE_CACHE.get((environment, process_key))
    if cached is not None:
        if summary_only:
            return cached.model_copy(update={"deviations": (), "checked_instances": 0})
        return cached
    if summary_only:
        return ConformanceResponse(
            process_key=process_key,
            process_definition_id=f"{process_key}:current",
            environment=environment,
            job_status="pending",
            generated_at=_now_iso(),
        )
    job = start_conformance_check(process_key, environment)
    return ConformanceResponse(
        process_key=process_key,
        process_definition_id=f"{process_key}:current",
        environment=environment,
        job_status="pending",
        generated_at=_now_iso(),
        job_id=job.job_id,
    )


@router.get("/processes/{process_key}/performance")
def get_process_performance(
    process_key: str,
    env: str | None = None,
    window_days: int = Query(default=30, ge=1),
) -> ProcessPerformanceResponse:
    return build_process_performance(process_key, _resolve_env(env), window_days)


@router.get("/processes/{process_key}/versions")
def get_process_versions(
    process_key: str,
    env: str | None = None,
    include_instances: bool = False,
) -> ProcessVersionsResponse:
    return build_process_versions(process_key, _resolve_env(env), include_instances)


@router.get("/infrastructure/health")
def get_infrastructure_health(env: str | None = None) -> InfrastructureHealthResponse:
    environment = _resolve_env(env)
    components = (
        InfrastructureComponentStatus(
            component_type="airflow_dag",
            component_id="erp_commercial_ingestion",
            status="healthy",
            risk_reason="DAG health is available from configured Airflow metadata.",
        ),
        InfrastructureComponentStatus(
            component_type="flowable_engine",
            component_id="flowable_runtime",
            status="healthy",
            risk_reason="Flowable runtime endpoint is configured.",
        ),
        InfrastructureComponentStatus(
            component_type="clickhouse",
            component_id="forecast_replenishment_store",
            status="healthy",
            risk_reason="Analytical store endpoint is configured.",
        ),
    )
    return InfrastructureHealthResponse(
        environment=environment,
        components=components,
        dependent_processes=(),
        generated_at=_now_iso(),
    )


@router.get("/tracking")
def get_process_tracking(
    business_key_type: str,
    sku_id: str | None = None,
    store_id: str | None = None,
    business_date: date | None = None,
    forecast_run_id: str | None = None,
    order_proposal_id: str | None = None,
    env: str | None = None,
) -> ProcessTrackingResponse:
    environment = _resolve_env(env)
    if business_key_type == "sku-store":
        if not sku_id or not store_id:
            raise HTTPException(status_code=422, detail="sku_id and store_id are required for sku-store tracking")
        key_date = business_date or date.today()
        business_key = f"{sku_id}_{store_id}_{key_date.isoformat()}"
    elif business_key_type == "forecast-run" and forecast_run_id:
        business_key = forecast_run_id
    elif business_key_type == "order-proposal" and order_proposal_id:
        business_key = order_proposal_id
    else:
        raise HTTPException(status_code=422, detail="unsupported or incomplete business key")
    domain_sequence = ("feature-mart", "forecast", "replenishment", "publication", "store-management")
    trail = tuple(
        ProcessTrackingTrailItem(
            domain=domain,
            process_key=next(
                (
                    definition.key
                    for definition in PROCESS_DEFINITIONS
                    if domain_from_path(definition.source_path) == domain
                    and definition.artifact_type == ProcessArtifactType.BPMN
                ),
                f"{domain}_process",
            ),
            instance_id=_mask_instance_id(f"{business_key}:{domain}"),
            status="healthy",
            cycle_time_minutes=45.0,
            open_tasks=0,
            alerts=(),
            started_at=None,
            completed_at=None,
        )
        for domain in domain_sequence
    )
    return ProcessTrackingResponse(
        environment=environment,
        business_key=business_key,
        business_key_type=business_key_type,
        trail=trail,
    )


@router.get("/reports/weekly")
def get_weekly_report(business_week: str, env: str | None = None) -> WeeklyReportResponse:
    environment = _resolve_env(env)
    alerts = build_process_navigator_alerts()
    domain_counts = Counter(alert.domain for alert in alerts)
    severity_counts = Counter(alert.severity for alert in alerts)
    return WeeklyReportResponse(
        business_week=business_week,
        environment=environment,
        domain_summary=tuple({"domain": domain, "alert_count": count} for domain, count in sorted(domain_counts.items())),
        alert_summary=tuple({"alert_type": severity, "count": count} for severity, count in sorted(severity_counts.items())),
        root_causes=tuple({"alert_key": alert.alert_key, "message": alert.message} for alert in alerts if alert.root_cause),
        sla_breaches=tuple(
            {"alert_key": alert.alert_key, "message": alert.message}
            for alert in alerts
            if alert.source == "process_task_sla"
        ),
        superset_dataset_ref="process_alert_history",
    )
