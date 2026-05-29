# IH-4 Completion Note

Status: completed  
Date: 2026-05-29  
Sprint: IH-4 Backup Restore Smoke

## Scope Completed

- Backup smoke script:
  - `scripts/dev/backup-smoke.ps1`;
  - default `plan` mode;
  - explicit `execute` mode;
  - PostgreSQL dump checksum;
  - ClickHouse backup command through configured database and backup disk.
- Restore smoke script:
  - `scripts/dev/restore-smoke.ps1`;
  - default `plan` mode;
  - explicit `execute` mode;
  - mandatory manifest path;
  - dedicated restore database variables;
  - checksum validation before restore.
- Configuration:
  - `OPEN_FNR_BACKUP_ROOT_PATH`;
  - `OPEN_FNR_BACKUP_RETENTION_DAYS`;
  - ClickHouse credentials/database entries in `.env.example`.
- Encoding/line endings:
  - PowerShell scripts are governed as UTF-8/LF through `.gitattributes`.
- Runbook:
  - `docs/runbooks/BACKUP_RESTORE_RUNBOOK.md`.

## Evidence

- Script architecture tests cover:
  - script existence;
  - central configuration variables;
  - checksum requirement;
  - restore safety guard;
  - no embedded network defaults.
- Targeted tests: 15 passed.
- Backup and restore plan-mode smoke passed through process-level PowerShell execution policy bypass.
- Full regression: 489 passed, 1 local `.pytest_cache` permission warning.

## Deferred

- Full production DR drill.
- Automated scheduled backup DAG/job.
- ClickHouse restore implementation for production-specific backup disk topology.

These are deferred to `DEP-4 Rollback And DR Drill` because IH-4 establishes the pilot smoke procedure and safety boundaries.
