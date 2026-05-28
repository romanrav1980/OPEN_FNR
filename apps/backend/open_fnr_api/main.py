from fastapi import FastAPI

from .config import settings
from .health import probe_http

app = FastAPI(
    title=settings.app_name,
    version=settings.version,
    description="OPEN FNR backend API skeleton.",
)


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
            "forecasting",
            "promo",
            "replenishment",
            "process-engine",
            "ui",
        ],
    }

