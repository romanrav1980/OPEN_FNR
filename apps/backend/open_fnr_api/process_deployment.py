from __future__ import annotations

import base64
import hashlib
import io
import json
from datetime import datetime, timezone
from enum import StrEnum
from pathlib import Path
from xml.etree import ElementTree
from zipfile import ZIP_DEFLATED, ZipFile
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from fastapi import APIRouter
from pydantic import BaseModel, Field

from .config import settings


router = APIRouter(prefix="/process-deployment", tags=["process-deployment"])

BPMN_NS = "http://www.omg.org/spec/BPMN/20100524/MODEL"
FLOWABLE_NS = "http://flowable.org/bpmn"


class ProcessArtifactType(StrEnum):
    BPMN = "bpmn"
    DMN = "dmn"
    CMMN = "cmmn"


class ProcessArtifactManifest(BaseModel):
    path: str
    artifact_type: ProcessArtifactType
    checksum_sha256: str
    size_bytes: int = Field(ge=0)


class ProcessDeploymentPackage(BaseModel):
    package_id: str
    artifact_root_path: str
    artifact_count: int = Field(ge=0)
    bpmn_count: int = Field(ge=0)
    dmn_count: int = Field(ge=0)
    cmmn_count: int = Field(ge=0)
    deployment_url: str
    deploy_channel: str
    created_at: datetime
    artifacts: tuple[ProcessArtifactManifest, ...]


class ProcessDeploymentRequest(BaseModel):
    execute: bool = False
    deployment_name: str = "OPEN_FNR_PROCESS_ARTIFACTS"
    runtime_safe_bpmn_only: bool = True


class ProcessDeploymentResult(BaseModel):
    package_id: str
    status: str
    execution_mode: str
    deployment_url: str
    deployment_id: str | None = None
    deployed_artifacts: int = Field(ge=0)
    http_status: int | None = None
    message: str


class ProcessDeployabilityIssue(BaseModel):
    path: str
    severity: str
    element_id: str
    message: str


class ProcessDeployabilityReport(BaseModel):
    package_id: str
    bpmn_total: int = Field(ge=0)
    bpmn_runtime_deployable: int = Field(ge=0)
    bpmn_requires_model_fix: int = Field(ge=0)
    dmn_governance_artifacts: int = Field(ge=0)
    cmmn_governance_artifacts: int = Field(ge=0)
    issues: tuple[ProcessDeployabilityIssue, ...]


class ProcessRuntimeStrategyItem(BaseModel):
    artifact_type: ProcessArtifactType
    runtime_target: str
    strategy: str
    artifact_count: int = Field(ge=0)
    status: str
    rationale: str
    next_gate: str


class ProcessRuntimeStrategyReport(BaseModel):
    package_id: str
    flowable_runtime_url: str
    items: tuple[ProcessRuntimeStrategyItem, ...]


class BpmnQualityIssue(BaseModel):
    path: str
    severity: str
    issue_type: str
    element_id: str
    message: str
    recommendation: str


class BpmnQualityReport(BaseModel):
    package_id: str
    bpmn_total: int = Field(ge=0)
    blocker_count: int = Field(ge=0)
    warning_count: int = Field(ge=0)
    cognitive_challenge_count: int = Field(ge=0)
    quality_gate: str
    issues: tuple[BpmnQualityIssue, ...]


ElementTree.register_namespace("", BPMN_NS)
ElementTree.register_namespace("flowable", FLOWABLE_NS)


def artifact_type_for_path(path: Path) -> ProcessArtifactType | None:
    name = path.name.lower()
    if name.endswith(".bpmn20.xml"):
        return ProcessArtifactType.BPMN
    if name.endswith(".dmn.xml"):
        return ProcessArtifactType.DMN
    if name.endswith(".cmmn.xml"):
        return ProcessArtifactType.CMMN
    return None


def checksum_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build_process_deployment_package(root_path: str | Path | None = None) -> ProcessDeploymentPackage:
    root = Path(root_path or settings.process_artifacts_root_path)
    artifacts: list[ProcessArtifactManifest] = []
    if root.exists():
        for path in sorted(root.rglob("*.xml")):
            artifact_type = artifact_type_for_path(path)
            if artifact_type is None or not path.is_file():
                continue
            artifacts.append(
                ProcessArtifactManifest(
                    path=path.as_posix(),
                    artifact_type=artifact_type,
                    checksum_sha256=checksum_file(path),
                    size_bytes=path.stat().st_size,
                )
            )
    bpmn_count = sum(1 for item in artifacts if item.artifact_type == ProcessArtifactType.BPMN)
    dmn_count = sum(1 for item in artifacts if item.artifact_type == ProcessArtifactType.DMN)
    cmmn_count = sum(1 for item in artifacts if item.artifact_type == ProcessArtifactType.CMMN)
    return ProcessDeploymentPackage(
        package_id="flowable-processes-v1",
        artifact_root_path=root.as_posix(),
        artifact_count=len(artifacts),
        bpmn_count=bpmn_count,
        dmn_count=dmn_count,
        cmmn_count=cmmn_count,
        deployment_url=settings.flowable_deployment_url,
        deploy_channel="flowable_rest",
        created_at=datetime(2026, 5, 29, 8, 0, tzinfo=timezone.utc),
        artifacts=tuple(artifacts),
    )


def normalize_bpmn_for_flowable_deployment(content: bytes) -> bytes:
    implementation_attrs = {
        "class",
        "delegateExpression",
        "type",
        "operation",
        "expression",
        f"{{{FLOWABLE_NS}}}class",
        f"{{{FLOWABLE_NS}}}delegateExpression",
        f"{{{FLOWABLE_NS}}}type",
        f"{{{FLOWABLE_NS}}}operation",
        f"{{{FLOWABLE_NS}}}expression",
    }
    tree = ElementTree.ElementTree(ElementTree.fromstring(content))
    root = tree.getroot()
    for task in root.findall(f".//{{{BPMN_NS}}}businessRuleTask"):
        task.tag = f"{{{BPMN_NS}}}serviceTask"
    for tag in ("serviceTask", "businessRuleTask"):
        for task in root.findall(f".//{{{BPMN_NS}}}{tag}"):
            if not any(attr in task.attrib for attr in implementation_attrs):
                task.set(f"{{{FLOWABLE_NS}}}delegateExpression", "${openFnrNoopDelegate}")
    output = io.BytesIO()
    tree.write(output, encoding="utf-8", xml_declaration=True)
    return output.getvalue()


def collect_bpmn_deployability_issues(path: Path) -> tuple[ProcessDeployabilityIssue, ...]:
    root = ElementTree.fromstring(path.read_bytes())
    sequence_flow_sources = {
        flow.attrib.get("sourceRef")
        for flow in root.findall(f".//{{{BPMN_NS}}}sequenceFlow")
        if flow.attrib.get("sourceRef")
    }
    issues: list[ProcessDeployabilityIssue] = []
    for gateway_tag in ("exclusiveGateway", "inclusiveGateway", "parallelGateway"):
        for gateway in root.findall(f".//{{{BPMN_NS}}}{gateway_tag}"):
            gateway_id = gateway.attrib.get("id", "")
            if gateway_id and gateway_id not in sequence_flow_sources:
                issues.append(
                    ProcessDeployabilityIssue(
                        path=path.as_posix(),
                        severity="blocker",
                        element_id=gateway_id,
                        message=f"{gateway_tag} has no outgoing sequence flow.",
                    )
                )
    return tuple(issues)


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


def collect_bpmn_quality_issues(path: Path) -> tuple[BpmnQualityIssue, ...]:
    root = ElementTree.fromstring(path.read_bytes())
    issues: list[BpmnQualityIssue] = []
    nodes: dict[str, tuple[str, str]] = {}
    duplicate_ids: set[str] = set()
    seen_ids: set[str] = set()
    for element in root.iter():
        element_id = element.attrib.get("id")
        if element_id:
            if element_id in seen_ids:
                duplicate_ids.add(element_id)
            seen_ids.add(element_id)
    for duplicate_id in sorted(duplicate_ids):
        issues.append(
            BpmnQualityIssue(
                path=path.as_posix(),
                severity="blocker",
                issue_type="duplicate_id",
                element_id=duplicate_id,
                message="BPMN element id is duplicated.",
                recommendation="Use stable unique ids for every BPMN element.",
            )
        )
    for tag in FLOW_NODE_TAGS:
        for element in root.findall(f".//{{{BPMN_NS}}}{tag}"):
            element_id = element.attrib.get("id")
            if element_id:
                nodes[element_id] = (tag, element.attrib.get("name", ""))
    incoming: dict[str, set[str]] = {node_id: set() for node_id in nodes}
    outgoing: dict[str, set[str]] = {node_id: set() for node_id in nodes}
    adjacency: dict[str, set[str]] = {node_id: set() for node_id in nodes}
    reverse_adjacency: dict[str, set[str]] = {node_id: set() for node_id in nodes}
    for flow in root.findall(f".//{{{BPMN_NS}}}sequenceFlow"):
        flow_id = flow.attrib.get("id", "")
        source = flow.attrib.get("sourceRef", "")
        target = flow.attrib.get("targetRef", "")
        if source not in nodes or target not in nodes:
            issues.append(
                BpmnQualityIssue(
                    path=path.as_posix(),
                    severity="blocker",
                    issue_type="invalid_sequence_reference",
                    element_id=flow_id,
                    message=f"Sequence flow references unknown node: {source} -> {target}.",
                    recommendation="Connect every sequence flow to existing BPMN flow nodes.",
                )
            )
            continue
        outgoing[source].add(flow_id)
        incoming[target].add(flow_id)
        adjacency[source].add(target)
        reverse_adjacency[target].add(source)
    starts = [node_id for node_id, (tag, _) in nodes.items() if tag == "startEvent"]
    ends = [node_id for node_id, (tag, _) in nodes.items() if tag == "endEvent"]
    if len(starts) != 1:
        issues.append(
            BpmnQualityIssue(
                path=path.as_posix(),
                severity="blocker",
                issue_type="start_event_count",
                element_id="process",
                message=f"Process must have exactly one start event; found {len(starts)}.",
                recommendation="Model one clear trigger per executable business process.",
            )
        )
    if not ends:
        issues.append(
            BpmnQualityIssue(
                path=path.as_posix(),
                severity="blocker",
                issue_type="missing_end_event",
                element_id="process",
                message="Process has no end event.",
                recommendation="Add explicit end states for success, rejection or escalation outcomes.",
            )
        )
    for node_id, (tag, name) in nodes.items():
        if tag != "startEvent" and not incoming[node_id]:
            issues.append(
                BpmnQualityIssue(
                    path=path.as_posix(),
                    severity="blocker",
                    issue_type="missing_incoming_flow",
                    element_id=node_id,
                    message=f"{tag} '{name}' has no incoming sequence flow.",
                    recommendation="Every non-start step must be reachable from the process trigger.",
                )
            )
        if tag != "endEvent" and not outgoing[node_id]:
            issues.append(
                BpmnQualityIssue(
                    path=path.as_posix(),
                    severity="blocker",
                    issue_type="missing_outgoing_flow",
                    element_id=node_id,
                    message=f"{tag} '{name}' has no outgoing sequence flow.",
                    recommendation="Every non-end step must have a next step or explicit terminal outcome.",
                )
            )
        if tag in {"exclusiveGateway", "inclusiveGateway"} and name.strip().endswith("?") and len(outgoing[node_id]) < 2:
            issues.append(
                BpmnQualityIssue(
                    path=path.as_posix(),
                    severity="blocker",
                    issue_type="question_gateway_without_alternative",
                    element_id=node_id,
                    message=f"Gateway '{name}' asks a question but has fewer than two outgoing paths.",
                    recommendation="Add explicit yes/no or accepted/rejected paths so the business decision is meaningful.",
                )
            )
        if tag == "userTask":
            issues.append(
                BpmnQualityIssue(
                    path=path.as_posix(),
                    severity="challenge",
                    issue_type="human_task_role_sla_audit",
                    element_id=node_id,
                    message=f"Human task '{name}' must have role, SLA and audit expectations in process documentation.",
                    recommendation="Verify candidate group, escalation SLA and audit event before production release.",
                )
            )
    if starts:
        reachable: set[str] = set()
        stack = list(starts)
        while stack:
            current = stack.pop()
            if current in reachable:
                continue
            reachable.add(current)
            stack.extend(adjacency[current] - reachable)
        for node_id in sorted(set(nodes) - reachable):
            issues.append(
                BpmnQualityIssue(
                    path=path.as_posix(),
                    severity="blocker",
                    issue_type="unreachable_node",
                    element_id=node_id,
                    message="BPMN node is not reachable from the start event.",
                    recommendation="Remove orphan branch or connect it to the intended business path.",
                )
            )
    if ends:
        can_reach_end: set[str] = set()
        stack = list(ends)
        while stack:
            current = stack.pop()
            if current in can_reach_end:
                continue
            can_reach_end.add(current)
            stack.extend(reverse_adjacency[current] - can_reach_end)
        for node_id in sorted(set(nodes) - can_reach_end):
            issues.append(
                BpmnQualityIssue(
                    path=path.as_posix(),
                    severity="blocker",
                    issue_type="dead_end_path",
                    element_id=node_id,
                    message="BPMN node cannot reach any end event.",
                    recommendation="Connect the path to a success, blocked, rejected or escalated end state.",
                )
            )
    has_audit_named_step = any("audit" in name.lower() for _, name in nodes.values())
    has_user_task = any(tag == "userTask" for tag, _ in nodes.values())
    if has_user_task and not has_audit_named_step:
        issues.append(
            BpmnQualityIssue(
                path=path.as_posix(),
                severity="challenge",
                issue_type="manual_decision_without_visible_audit",
                element_id="process",
                message="Process has human tasks but no visibly named audit step.",
                recommendation="Confirm audit is implemented by engine listener, service task or backend event.",
            )
        )
    return tuple(issues)


def build_bpmn_quality_report(root_path: str | Path | None = None) -> BpmnQualityReport:
    package = build_process_deployment_package(root_path)
    issues: list[BpmnQualityIssue] = []
    for artifact in package.artifacts:
        if artifact.artifact_type == ProcessArtifactType.BPMN:
            issues.extend(collect_bpmn_quality_issues(Path(artifact.path)))
    blocker_count = sum(1 for issue in issues if issue.severity == "blocker")
    warning_count = sum(1 for issue in issues if issue.severity == "warning")
    cognitive_challenge_count = sum(1 for issue in issues if issue.severity == "challenge")
    return BpmnQualityReport(
        package_id=package.package_id,
        bpmn_total=package.bpmn_count,
        blocker_count=blocker_count,
        warning_count=warning_count,
        cognitive_challenge_count=cognitive_challenge_count,
        quality_gate="passed" if blocker_count == 0 else "blocked",
        issues=tuple(issues),
    )


def build_process_deployability_report(root_path: str | Path | None = None) -> ProcessDeployabilityReport:
    package = build_process_deployment_package(root_path)
    issues: list[ProcessDeployabilityIssue] = []
    bpmn_runtime_deployable = 0
    for artifact in package.artifacts:
        if artifact.artifact_type != ProcessArtifactType.BPMN:
            continue
        artifact_issues = collect_bpmn_deployability_issues(Path(artifact.path))
        issues.extend(artifact_issues)
        if not artifact_issues:
            bpmn_runtime_deployable += 1
    return ProcessDeployabilityReport(
        package_id=package.package_id,
        bpmn_total=package.bpmn_count,
        bpmn_runtime_deployable=bpmn_runtime_deployable,
        bpmn_requires_model_fix=package.bpmn_count - bpmn_runtime_deployable,
        dmn_governance_artifacts=package.dmn_count,
        cmmn_governance_artifacts=package.cmmn_count,
        issues=tuple(issues),
    )


def build_process_runtime_strategy_report(root_path: str | Path | None = None) -> ProcessRuntimeStrategyReport:
    package = build_process_deployment_package(root_path)
    deployability = build_process_deployability_report(root_path)
    return ProcessRuntimeStrategyReport(
        package_id=package.package_id,
        flowable_runtime_url=package.deployment_url,
        items=(
            ProcessRuntimeStrategyItem(
                artifact_type=ProcessArtifactType.BPMN,
                runtime_target="flowable_process_engine",
                strategy="runtime_deploy",
                artifact_count=deployability.bpmn_runtime_deployable,
                status="ready",
                rationale="BPMN processes are normalized into a runtime-safe .bar package and accepted by Flowable REST.",
                next_gate="redeploy_on_process_change",
            ),
            ProcessRuntimeStrategyItem(
                artifact_type=ProcessArtifactType.DMN,
                runtime_target="open_fnr_governance_package",
                strategy="governed_artifact",
                artifact_count=package.dmn_count,
                status="governed_not_runtime_deployed",
                rationale=(
                    "Current Flowable REST image rejected combined DMN runtime upload with a missing KIE runtime "
                    "dependency; OPEN FNR keeps DMN versioned and tested as governed decision artifacts until a "
                    "dedicated DMN runtime route is enabled."
                ),
                next_gate="dmn_runtime_adapter_decision",
            ),
            ProcessRuntimeStrategyItem(
                artifact_type=ProcessArtifactType.CMMN,
                runtime_target="open_fnr_governance_package",
                strategy="governed_artifact",
                artifact_count=package.cmmn_count,
                status="governed_not_runtime_deployed",
                rationale=(
                    "CMMN case models remain versioned governance artifacts while case execution behavior is "
                    "represented through OPEN FNR API tests and UI process evidence."
                ),
                next_gate="cmmn_runtime_adapter_decision",
            ),
        ),
    )


def build_flowable_bar_archive(package: ProcessDeploymentPackage, runtime_safe_bpmn_only: bool = True) -> bytes:
    root = Path(package.artifact_root_path)
    deployability_report = build_process_deployability_report(root)
    blocked_paths = {issue.path for issue in deployability_report.issues}
    manifest = {
        "package_id": package.package_id,
        "artifact_count": package.artifact_count,
        "created_at": package.created_at.isoformat(),
        "runtime_safe_bpmn_only": runtime_safe_bpmn_only,
        "deployability": deployability_report.model_dump(mode="json"),
        "artifacts": [artifact.model_dump(mode="json") for artifact in package.artifacts],
    }
    output = io.BytesIO()
    with ZipFile(output, mode="w", compression=ZIP_DEFLATED) as archive:
        archive.writestr("open-fnr-deployment-manifest.json", json.dumps(manifest, ensure_ascii=True, indent=2))
        for artifact in package.artifacts:
            if runtime_safe_bpmn_only and artifact.artifact_type != ProcessArtifactType.BPMN:
                continue
            if runtime_safe_bpmn_only and artifact.path in blocked_paths:
                continue
            source_path = Path(artifact.path)
            archive_name = source_path.relative_to(root).as_posix() if source_path.is_relative_to(root) else source_path.name
            content = source_path.read_bytes()
            if artifact.artifact_type == ProcessArtifactType.BPMN:
                content = normalize_bpmn_for_flowable_deployment(content)
            archive.writestr(archive_name, content)
    return output.getvalue()


def build_multipart_deployment_body(
    package: ProcessDeploymentPackage,
    deployment_name: str,
    boundary: str = "open-fnr-flowable-boundary",
    runtime_safe_bpmn_only: bool = True,
) -> bytes:
    body = bytearray()

    def add_field(name: str, value: str) -> None:
        body.extend(f"--{boundary}\r\n".encode("utf-8"))
        body.extend(f'Content-Disposition: form-data; name="{name}"\r\n\r\n'.encode("utf-8"))
        body.extend(value.encode("utf-8"))
        body.extend(b"\r\n")

    def add_file(field_name: str, file_name: str, content: bytes) -> None:
        body.extend(f"--{boundary}\r\n".encode("utf-8"))
        body.extend(
            (
                f'Content-Disposition: form-data; name="{field_name}"; '
                f'filename="{file_name}"\r\n'
                "Content-Type: application/octet-stream\r\n\r\n"
            ).encode("utf-8")
        )
        body.extend(content)
        body.extend(b"\r\n")

    add_field("deploymentName", deployment_name)
    add_field("tenantId", "open-fnr")
    add_file(
        "file",
        "open-fnr-processes.bar",
        build_flowable_bar_archive(package, runtime_safe_bpmn_only=runtime_safe_bpmn_only),
    )
    body.extend(f"--{boundary}--\r\n".encode("utf-8"))
    return bytes(body)


def deploy_process_package_to_flowable(
    package: ProcessDeploymentPackage,
    deployment_name: str,
    runtime_safe_bpmn_only: bool = True,
    opener=urlopen,
) -> ProcessDeploymentResult:
    boundary = "open-fnr-flowable-boundary"
    body = build_multipart_deployment_body(
        package,
        deployment_name=deployment_name,
        boundary=boundary,
        runtime_safe_bpmn_only=runtime_safe_bpmn_only,
    )
    deployability_report = build_process_deployability_report(package.artifact_root_path)
    request = Request(
        package.deployment_url,
        data=body,
        method="POST",
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
    )
    if settings.flowable_rest_username or settings.flowable_rest_password:
        token = f"{settings.flowable_rest_username}:{settings.flowable_rest_password}".encode("utf-8")
        request.add_header("Authorization", f"Basic {base64.b64encode(token).decode('ascii')}")
    try:
        with opener(request, timeout=settings.flowable_http_timeout_seconds) as response:
            payload = json.loads(response.read().decode("utf-8") or "{}")
            return ProcessDeploymentResult(
                package_id=package.package_id,
                status="deployed",
                execution_mode="execute",
                deployment_url=package.deployment_url,
                deployment_id=payload.get("id"),
                deployed_artifacts=deployability_report.bpmn_runtime_deployable
                if runtime_safe_bpmn_only
                else package.artifact_count,
                http_status=getattr(response, "status", None),
                message="Flowable deployment accepted the artifact package.",
            )
    except HTTPError as error:
        return ProcessDeploymentResult(
            package_id=package.package_id,
            status="failed",
            execution_mode="execute",
            deployment_url=package.deployment_url,
            deployed_artifacts=0,
            http_status=error.code,
            message=f"Flowable deployment rejected the package: HTTP {error.code}.",
        )
    except URLError as error:
        return ProcessDeploymentResult(
            package_id=package.package_id,
            status="failed",
            execution_mode="execute",
            deployment_url=package.deployment_url,
            deployed_artifacts=0,
            message=f"Flowable deployment unavailable: {error.reason}.",
        )


@router.get("/packages/current", response_model=ProcessDeploymentPackage)
def get_current_process_deployment_package() -> ProcessDeploymentPackage:
    return build_process_deployment_package()


@router.post("/packages/current/validate", response_model=ProcessDeploymentPackage)
def validate_current_process_deployment_package() -> ProcessDeploymentPackage:
    return build_process_deployment_package()


@router.get("/packages/current/deployability", response_model=ProcessDeployabilityReport)
def get_current_process_deployability_report() -> ProcessDeployabilityReport:
    return build_process_deployability_report()


@router.get("/packages/current/runtime-strategy", response_model=ProcessRuntimeStrategyReport)
def get_current_process_runtime_strategy_report() -> ProcessRuntimeStrategyReport:
    return build_process_runtime_strategy_report()


@router.get("/packages/current/bpmn-quality", response_model=BpmnQualityReport)
def get_current_bpmn_quality_report() -> BpmnQualityReport:
    return build_bpmn_quality_report()


@router.post("/packages/current/deploy", response_model=ProcessDeploymentResult)
def deploy_current_process_deployment_package(request: ProcessDeploymentRequest) -> ProcessDeploymentResult:
    package = build_process_deployment_package()
    deployability_report = build_process_deployability_report(package.artifact_root_path)
    if not request.execute:
        return ProcessDeploymentResult(
            package_id=package.package_id,
            status="validated",
            execution_mode="dry_run",
            deployment_url=package.deployment_url,
            deployed_artifacts=0,
            message=(
                f"Dry run validated {package.artifact_count} governance artifacts and "
                f"{deployability_report.bpmn_runtime_deployable} runtime-deployable BPMN files. "
                "Set execute=true to upload the runtime-safe Flowable package."
            ),
        )
    return deploy_process_package_to_flowable(
        package,
        deployment_name=request.deployment_name,
        runtime_safe_bpmn_only=request.runtime_safe_bpmn_only,
    )
