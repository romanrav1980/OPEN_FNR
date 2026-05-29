# OPEN FNR Backup Restore Smoke Runbook

Status: pilot readiness runbook  
Date: 2026-05-29  
Related sprint: IH-4 Backup Restore Smoke

## Purpose

This runbook defines the repeatable backup and restore smoke procedure for PostgreSQL and ClickHouse before pilot operations. The goal is not a full disaster-recovery drill; it is a lightweight evidence step proving that backup artifacts can be created, checksummed and restored into dedicated smoke databases.

## Configuration

All paths and network settings come from project configuration:

| Setting | Purpose |
| --- | --- |
| `OPEN_FNR_BACKUP_ROOT_PATH` | Root folder for backup-smoke artifacts. |
| `OPEN_FNR_BACKUP_RETENTION_DAYS` | Local retention window for smoke artifacts. |
| `OPEN_FNR_POSTGRES_HOST` | PostgreSQL host from central config. |
| `OPEN_FNR_POSTGRES_PORT` | PostgreSQL port from central config. |
| `OPEN_FNR_POSTGRES_DATABASE` | Source PostgreSQL database. |
| `OPEN_FNR_POSTGRES_USER` | PostgreSQL backup user. |
| `OPEN_FNR_CLICKHOUSE_HOST` | ClickHouse host from central config. |
| `OPEN_FNR_CLICKHOUSE_HTTP_PORT` | ClickHouse port from central config. |
| `OPEN_FNR_CLICKHOUSE_DATABASE` | Source ClickHouse database. |
| `OPEN_FNR_CLICKHOUSE_BACKUP_DISK` | Configured ClickHouse backup disk name. |
| `OPEN_FNR_RESTORE_POSTGRES_DATABASE` | Dedicated PostgreSQL restore-smoke database. |
| `OPEN_FNR_RESTORE_CLICKHOUSE_DATABASE` | Dedicated ClickHouse restore-smoke database. |

No host name, IP address, port number or service URL may be embedded in the scripts.

## Backup Smoke

1. Run the plan first:

```powershell
.\scripts\dev\backup-smoke.ps1 -Mode plan
```

If local PowerShell execution policy blocks unsigned scripts, run the same command through a one-time process-level bypass:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\dev\backup-smoke.ps1 -Mode plan
```

2. Review required environment variables and target artifact path.
3. Run execute mode only after the configured environment has been verified:

```powershell
.\scripts\dev\backup-smoke.ps1 -Mode execute
```

Expected result:

- PostgreSQL custom-format dump is created.
- ClickHouse backup command is executed against the configured database and backup disk.
- `backup_manifest.json` is written with creation timestamp, PostgreSQL checksum and ClickHouse backup metadata.

## Restore Smoke

1. Run the plan first:

```powershell
.\scripts\dev\restore-smoke.ps1 -Mode plan
```

If local PowerShell execution policy blocks unsigned scripts, run the same command through a one-time process-level bypass:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\dev\restore-smoke.ps1 -Mode plan
```

2. Create or select dedicated smoke restore databases through controlled DBA procedure.
3. Set `OPEN_FNR_RESTORE_POSTGRES_DATABASE` and `OPEN_FNR_RESTORE_CLICKHOUSE_DATABASE`.
4. Execute restore smoke with a manifest:

```powershell
.\scripts\dev\restore-smoke.ps1 -Mode execute -ManifestPath <backup_manifest_path>
```

Expected result:

- Manifest checksum is verified before restore.
- PostgreSQL dump is restored into the dedicated restore database.
- ClickHouse restore-smoke database is prepared for restore validation.
- The script emits JSON evidence with restored timestamp and verified checksum flag.

## RPO/RTO Evidence Template

| Evidence | Value |
| --- | --- |
| Backup started at | To be captured from command log. |
| Backup finished at | To be captured from command log. |
| Restore started at | To be captured from command log. |
| Restore finished at | To be captured from command log. |
| PostgreSQL dump checksum | From `backup_manifest.json`. |
| PostgreSQL smoke restore result | Pass/fail. |
| ClickHouse backup result | Pass/fail. |
| ClickHouse smoke restore result | Pass/fail or deferred with reason. |
| RPO observed | Difference between backup timestamp and latest committed business event. |
| RTO observed | Restore duration. |

## Degraded Mode Checklist

If restore smoke fails:

- stop publication and controlled exports;
- keep forecast and replenishment calculations in read-only review mode;
- create a process task for platform owner and DBA;
- attach backup manifest, command log and failing step;
- decide whether the pilot can continue in shadow mode only;
- record the decision in operational audit.

## Acceptance Gate

IH-4 is accepted when:

- backup and restore scripts have plan mode by default;
- execute mode uses only central configuration;
- backup manifest includes checksum;
- restore smoke verifies checksum before restore;
- runbook and tests are committed;
- quality gates pass.
