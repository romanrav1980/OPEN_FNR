# OPEN FNR API Error Registry

Status: initial registry required by `TECHNICAL_SPEC_SUPPLEMENT_1.md`.

All public API errors must use:

```json
{
  "error_code": "ERROR_CODE",
  "message": "Human readable message",
  "request_id": "uuid",
  "timestamp": "2026-06-01T08:00:00Z",
  "docs_url": "/docs/errors/ERROR_CODE"
}
```

| Error code | HTTP status | Meaning | Owner |
| --- | --- | --- | --- |
| `SOURCE_SLA_BREACH` | 409 | Source data missed SLA/cutoff or completeness threshold | Data Platform Owner |
| `FORECAST_NOT_FOUND` | 404 | Forecast for requested scope/version is absent | Forecast Owner |
| `ORDER_PROPOSAL_BLOCKED` | 409 | Order proposal cannot be published without approval | Supply Chain Owner |
| `SUPPLIER_SCOPE_DENIED` | 403 | Supplier tried to access another supplier scope | Security Owner |
| `MODEL_RELEASE_GATE_FAILED` | 409 | Candidate model failed release criteria | DS Lead |
| `API_VERSION_DEPRECATED` | 410 | API version has passed sunset date | API Owner |
| `IDP_NOT_READY` | 409 | Stage/prod IdP configuration is incomplete | Security Owner |
