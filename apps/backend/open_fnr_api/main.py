from fastapi import FastAPI

from .adjustments import router as adjustments_router
from .audit import router as audit_router
from .capacity import router as capacity_router
from .config import settings
from .clean_publication import router as clean_publication_router
from .data_quality import router as data_quality_router
from .data_scale import router as data_scale_router
from .diagnostics import router as diagnostics_router
from .exceptions import router as exceptions_router
from .feature_mart import router as feature_mart_router
from .forecast import router as forecast_router
from .ml_models import router as ml_models_router
from .ml_governance import router as ml_governance_router
from .multi_echelon import router as multi_echelon_router
from .observability import router as observability_router
from .performance import router as performance_router
from .pilot import router as pilot_router
from .process_engine import router as process_engine_router
from .process_governance import router as process_governance_router
from .promo import router as promo_router
from .procurement import router as procurement_router
from .publication import router as publication_router
from .release_gate import router as release_gate_router
from .replenishment import router as replenishment_router
from .replenishment_scale import router as replenishment_scale_router
from .security import router as security_router
from .shelf_space import router as shelf_space_router
from .shadow_gate import router as shadow_gate_router
from .stage import router as stage_router
from .store_management import router as store_management_router
from .supplier_collaboration import router as supplier_collaboration_router
from .health import probe_http
from .ingestion import router as ingestion_router
from .kpi import router as kpi_router
from .lifecycle import router as lifecycle_router
from .marts import router as marts_router

app = FastAPI(
    title=settings.app_name,
    version=settings.version,
    description="OPEN FNR backend API skeleton.",
)

app.include_router(ingestion_router)
app.include_router(clean_publication_router)
app.include_router(adjustments_router)
app.include_router(audit_router)
app.include_router(capacity_router)
app.include_router(data_quality_router)
app.include_router(data_scale_router)
app.include_router(diagnostics_router)
app.include_router(exceptions_router)
app.include_router(feature_mart_router)
app.include_router(forecast_router)
app.include_router(ml_models_router)
app.include_router(ml_governance_router)
app.include_router(multi_echelon_router)
app.include_router(observability_router)
app.include_router(performance_router)
app.include_router(pilot_router)
app.include_router(promo_router)
app.include_router(procurement_router)
app.include_router(publication_router)
app.include_router(release_gate_router)
app.include_router(process_engine_router)
app.include_router(process_governance_router)
app.include_router(replenishment_router)
app.include_router(replenishment_scale_router)
app.include_router(kpi_router)
app.include_router(lifecycle_router)
app.include_router(marts_router)
app.include_router(security_router)
app.include_router(shelf_space_router)
app.include_router(shadow_gate_router)
app.include_router(stage_router)
app.include_router(store_management_router)
app.include_router(supplier_collaboration_router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "version": settings.version}


@app.get("/ready")
def ready() -> dict[str, object]:
    probes = [probe_http(endpoint) for endpoint in settings.service_endpoints()]
    overall = "ok" if all(probe.status == "ok" for probe in probes) else "degraded"
    return {
        "status": overall,
        "services": [probe.__dict__ for probe in probes],
    }


@app.get("/metadata")
def metadata() -> dict[str, object]:
    return {
        "name": settings.app_name,
        "version": settings.version,
        "runtime_mode": settings.runtime_mode,
        "mock_mode": settings.mock_mode,
        "audit_enabled": settings.audit_enabled,
        "modules": [
            "audit",
            "data-platform",
            "capacity",
            "clean-publication",
            "data-ingestion",
            "data-quality",
            "production-data-scale",
            "diagnostics",
            "feature-mart",
            "forecasting",
            "ml-models",
            "ml-governance",
            "marts",
            "promo",
            "procurement",
            "replenishment",
            "replenishment-scale",
            "release-gate",
            "multi-echelon",
            "observability",
            "performance",
            "business-pilot",
            "security",
            "shelf-space",
            "shadow-load-gate",
            "stage-rehearsal",
            "store-management",
            "supplier-collaboration",
            "process-engine",
            "process-governance",
            "ui",
        ],
    }
