from fastapi import APIRouter

from .mart_repositories import mart_metadata_repository


router = APIRouter(prefix="/marts", tags=["marts"])


@router.get("/clickhouse")
def list_clickhouse_marts() -> dict[str, object]:
    tables = mart_metadata_repository.list_tables()
    return {
        "items": [table.__dict__ for table in tables],
        "total": len(tables),
        "storage": "clickhouse",
    }
