$ErrorActionPreference = "Stop"

$env:PYTHONPATH = "apps/backend"
python -m uvicorn open_fnr_api.main:app --host 127.0.0.1 --port 8000 --reload
