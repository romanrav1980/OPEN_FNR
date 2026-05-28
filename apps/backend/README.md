# OPEN FNR Backend

FastAPI backend skeleton for Sprint 0.

## Run

```powershell
python -m uvicorn open_fnr_api.main:app --app-dir apps/backend --host 127.0.0.1 --port 8000
```

## Endpoints

| Endpoint | Purpose |
| --- | --- |
| `/health` | process health |
| `/ready` | dev infrastructure readiness probes |
| `/metadata` | basic module metadata |

