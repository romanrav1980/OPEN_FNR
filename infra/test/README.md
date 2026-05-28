# OPEN FNR Test Environment

The test contour reuses the common Docker Compose definition from `infra/dev/compose.yaml` with a separate environment file and isolated project name.

## Start

```powershell
docker compose --env-file infra/test/.env.example -f infra/dev/compose.yaml up -d
```

## Stop

```powershell
docker compose --env-file infra/test/.env.example -f infra/dev/compose.yaml down
```

## Purpose

- automated integration testing;
- API and process regression;
- ingestion pipeline validation on synthetic or masked data;
- UI E2E tests before stage.

Network ports are configured only in `infra/test/.env.example`.
