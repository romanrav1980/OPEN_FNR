from fastapi import FastAPI

from .config import settings
from .data_quality import router as data_quality_router
from .exceptions import router as exceptions_router
from .feature_mart import router as feature_mart_router
from .forecast import router as forecast_router
from .ml_models import router as ml_models_router
from .process_engine import router as process_engine_router
from .promo import router as promo_router
from .replenishment import router as replenishment_router
from .health import probe_http
from .ingestion import router as ingestion_router

app = FastAPI(
    title=settings.app_name,
    version=settings.version,
    description="OPEN FNR backend API skeleton.",
)

app.include_router(ingestion_router)
app.include_router(data_quality_router)
app.include_router(exceptions_router)
app.include_router(feature_mart_router)
app.include_router(forecast_router)
app.include_router(ml_models_router)
app.include_router(promo_router)
app.include_router(process_engine_router)
app.include_router(replenishment_router)


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
        "modules": [
            "data-platform",
            "data-ingestion",
            "data-quality",
            "feature-mart",
            "forecasting",
            "ml-models",
            "promo",
            "replenishment",
            "process-engine",
            "ui",
        ],
    }
