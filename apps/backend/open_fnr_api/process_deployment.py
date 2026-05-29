from __future__ import annotations

import hashlib
import json
import base64
from datetime import datetime, timezone
from enum import StrEnum
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from fastapi import APIRouter
from pydantic import BaseModel, Field

from .config import settings


router = APIRouter(prefix="/process-deployment", tags=["process-deployment"])


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


class ProcessDeploymentResult(BaseModel):
    package_id: str
    status: str
    execution_mode: str
    deployment_url: str
    deployment_id: str | None = None
    deployed_artifacts: int = Field(ge=0)
    http_status: int | None = None
    message: str


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


def build_multipart_deployment_body(
    package: ProcessDeploymentPackage,
    deployment_name: str,
    boundary: str = "open-fnr-flowable-boundary",
) -> bytes:
    body = bytearray()

    def add_field(name: str, value: str) -> None:
        body.extend(f"--{boundary}\r\n".encode("utf-8"))
        body.extend(f'Content-Disposition: form-data; name="{name}"\r\n\r\n'.encode("utf-8"))
        body.extend(value.encode("utf-8"))
        body.extend(b"\r\n")

    def add_file(field_name: str, file_path: Path) -> None:
        body.extend(f"--{boundary}\r\n".encode("utf-8"))
        body.extend(
            (
                f'Content-Disposition: form-data; name="{field_name}"; '
                f'filename="{file_path.name}"\r\n'
                "Content-Type: text/xml\r\n\r\n"
            ).encode("utf-8")
        )
        body.extend(file_path.read_bytes())
        body.extend(b"\r\n")

    add_field("deploymentName", deployment_name)
    add_field("tenantId", "open-fnr")
    for artifact in package.artifacts:
        add_file("file", Path(artifact.path))
    body.extend(f"--{boundary}--\r\n".encode("utf-8"))
    return bytes(body)


def deploy_process_package_to_flowable(
    package: ProcessDeploymentPackage,
    deployment_name: str,
    opener=urlopen,
) -> ProcessDeploymentResult:
    boundary = "open-fnr-flowable-boundary"
    body = build_multipart_deployment_body(package, deployment_name=deployment_name, boundary=boundary)
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
                deployed_artifacts=package.artifact_count,
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


@router.post("/packages/current/deploy", response_model=ProcessDeploymentResult)
def deploy_current_process_deployment_package(request: ProcessDeploymentRequest) -> ProcessDeploymentResult:
    package = build_process_deployment_package()
    if not request.execute:
        return ProcessDeploymentResult(
            package_id=package.package_id,
            status="validated",
            execution_mode="dry_run",
            deployment_url=package.deployment_url,
            deployed_artifacts=0,
            message=(
                f"Dry run validated {package.artifact_count} artifacts. "
                "Set execute=true to upload BPMN/DMN/CMMN artifacts to Flowable."
            ),
        )
    return deploy_process_package_to_flowable(package, deployment_name=request.deployment_name)
