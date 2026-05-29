from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from enum import StrEnum
from pathlib import Path

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


@router.get("/packages/current", response_model=ProcessDeploymentPackage)
def get_current_process_deployment_package() -> ProcessDeploymentPackage:
    return build_process_deployment_package()


@router.post("/packages/current/validate", response_model=ProcessDeploymentPackage)
def validate_current_process_deployment_package() -> ProcessDeploymentPackage:
    return build_process_deployment_package()
