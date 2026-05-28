# OPEN FNR Stage Environment

The stage contour reuses the common Docker Compose definition from `infra/dev/compose.yaml` with a separate environment file and isolated project name.

## Start

```powershell
docker compose --env-file infra/stage/.env.example -f infra/dev/compose.yaml up -d
```

## Stop

```powershell
docker compose --env-file infra/stage/.env.example -f infra/dev/compose.yaml down
```

## Purpose

- business UAT;
- realistic integration rehearsals;
- release candidate validation;
- process engine deployment checks;
- pilot readiness checks.

Network ports are configured only in `infra/stage/.env.example`.
