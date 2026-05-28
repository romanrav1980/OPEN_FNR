from __future__ import annotations

from dataclasses import dataclass
from time import perf_counter
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from .config import ServiceEndpoint


@dataclass(frozen=True)
class ProbeResult:
    name: str
    status: str
    latency_ms: int
    detail: str


def probe_http(endpoint: ServiceEndpoint, timeout_seconds: float = 2.0) -> ProbeResult:
    started = perf_counter()
    request = Request(endpoint.url, method="GET")
    try:
        with urlopen(request, timeout=timeout_seconds) as response:
            status_code = response.status
            detail = f"HTTP {status_code}"
    except HTTPError as exc:
        status_code = exc.code
        detail = f"HTTP {status_code}"
    except URLError as exc:
        latency_ms = int((perf_counter() - started) * 1000)
        return ProbeResult(endpoint.name, "down", latency_ms, str(exc.reason))
    except TimeoutError:
        latency_ms = int((perf_counter() - started) * 1000)
        return ProbeResult(endpoint.name, "down", latency_ms, "timeout")

    latency_ms = int((perf_counter() - started) * 1000)
    status = "ok" if status_code in endpoint.required_statuses else "degraded"
    return ProbeResult(endpoint.name, status, latency_ms, detail)

