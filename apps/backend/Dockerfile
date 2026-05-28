FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

WORKDIR /app

RUN pip install --no-cache-dir \
    "fastapi>=0.118.0" \
    "uvicorn[standard]>=0.30.0" \
    "pydantic>=2.0.0" \
    "pg8000>=1.31.0"

COPY apps/backend/open_fnr_api /app/open_fnr_api

EXPOSE 8000

CMD ["uvicorn", "open_fnr_api.main:app", "--host", "0.0.0.0", "--port", "8000"]
