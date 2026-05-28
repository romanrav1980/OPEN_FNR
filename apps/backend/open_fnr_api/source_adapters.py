from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Protocol

from pydantic import BaseModel, Field

from .config import settings


SUPPORTED_SOURCE_EXTENSIONS = {".csv", ".json", ".parquet"}


class SourceFile(BaseModel):
    source_system: str = Field(min_length=1, max_length=64)
    contract_name: str = Field(min_length=1, max_length=128)
    business_date: date
    file_name: str = Field(min_length=1, max_length=255)
    file_uri: str = Field(min_length=1, max_length=1024)
    size_bytes: int = Field(ge=0)


class SourceAdapter(Protocol):
    def discover(self, source_system: str, contract_name: str, business_date: date) -> tuple[SourceFile, ...]:
        ...


class LocalFileDropAdapter:
    def __init__(self, landing_root_path: str | Path | None = None) -> None:
        self.landing_root_path = Path(landing_root_path or settings.landing_root_path)

    def discover(self, source_system: str, contract_name: str, business_date: date) -> tuple[SourceFile, ...]:
        source_dir = (
            self.landing_root_path
            / source_system.lower()
            / contract_name
            / f"business_date={business_date.isoformat()}"
        )
        if not source_dir.exists():
            return ()

        files: list[SourceFile] = []
        for path in sorted(source_dir.iterdir()):
            if not path.is_file() or path.suffix.lower() not in SUPPORTED_SOURCE_EXTENSIONS:
                continue
            files.append(
                SourceFile(
                    source_system=source_system.upper(),
                    contract_name=contract_name,
                    business_date=business_date,
                    file_name=path.name,
                    file_uri=path.as_posix(),
                    size_bytes=path.stat().st_size,
                )
            )
        return tuple(files)
