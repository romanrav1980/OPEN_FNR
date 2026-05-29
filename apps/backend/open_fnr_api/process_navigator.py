from __future__ import annotations

from collections import Counter, defaultdict
from pathlib import Path
from xml.etree import ElementTree

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

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
    node_count: int = Field(ge=0)
    edge_count: int = Field(ge=0)
    nodes: tuple[ProcessMapNode, ...]
    edges: tuple[ProcessMapEdge, ...]
    legend: dict[str, str]


class ProcessNavigatorAlert(BaseModel):
    alert_id: str
    severity: str
    domain: str
    process_key: str | None
    source: str
    message: str
    recommended_action: str
    status: str


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


def build_process_navigator_alerts() -> tuple[ProcessNavigatorAlert, ...]:
    quality = build_bpmn_quality_report()
    alerts: list[ProcessNavigatorAlert] = []
    for issue in quality.issues:
        process_key = process_key_from_artifact_path(issue.path)
        alerts.append(
            ProcessNavigatorAlert(
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
                ProcessNavigatorAlert(
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


def build_process_map(zoom_level: int = 1) -> ProcessMapResponse:
    zoom_level = max(0, min(4, zoom_level))
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


def build_process_drilldown(process_key: str) -> ProcessDrilldownResponse:
    definition = next((item for item in PROCESS_DEFINITIONS if item.key == process_key), None)
    if definition is None:
        raise HTTPException(status_code=404, detail="process definition not found")
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


@router.get("/map")
def get_process_map(zoom: int = Query(default=1, ge=0, le=4)) -> ProcessMapResponse:
    return build_process_map(zoom)


@router.get("/alerts")
def get_process_alerts() -> dict[str, tuple[ProcessNavigatorAlert, ...]]:
    return {"items": build_process_navigator_alerts()}


@router.get("/processes/{process_key}/drilldown")
def get_process_drilldown(process_key: str) -> ProcessDrilldownResponse:
    return build_process_drilldown(process_key)
