param(
    [ValidateSet("plan", "execute")]
    [string]$Mode = "plan"
)

$ErrorActionPreference = "Stop"

function Require-Env {
    param([string]$Name)
    $value = [Environment]::GetEnvironmentVariable($Name)
    if ([string]::IsNullOrWhiteSpace($value)) {
        throw "Required environment variable is missing: $Name"
    }
    return $value
}

$backupRoot = if ($env:OPEN_FNR_BACKUP_ROOT_PATH) { $env:OPEN_FNR_BACKUP_ROOT_PATH } else { "backups/open_fnr" }
$timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$targetDir = Join-Path $backupRoot $timestamp

$plan = [ordered]@{
    mode = $Mode
    purpose = "Create PostgreSQL and ClickHouse backup-smoke artifacts using project configuration."
    target_dir = $targetDir
    required_env = @(
        "OPEN_FNR_POSTGRES_HOST",
        "OPEN_FNR_POSTGRES_PORT",
        "OPEN_FNR_POSTGRES_DATABASE",
        "OPEN_FNR_POSTGRES_USER",
        "OPEN_FNR_CLICKHOUSE_HOST",
        "OPEN_FNR_CLICKHOUSE_HTTP_PORT",
        "OPEN_FNR_CLICKHOUSE_DATABASE"
    )
    postgres = [ordered]@{
        command = "pg_dump --format=custom --file <target>/postgres_open_fnr.dump"
        host_env = "OPEN_FNR_POSTGRES_HOST"
        port_env = "OPEN_FNR_POSTGRES_PORT"
        database_env = "OPEN_FNR_POSTGRES_DATABASE"
        user_env = "OPEN_FNR_POSTGRES_USER"
    }
    clickhouse = [ordered]@{
        command = "clickhouse-client --query BACKUP DATABASE <configured_db> TO Disk(<configured_backup_disk>, <generated_backup_name>)"
        host_env = "OPEN_FNR_CLICKHOUSE_HOST"
        port_env = "OPEN_FNR_CLICKHOUSE_HTTP_PORT"
        database_env = "OPEN_FNR_CLICKHOUSE_DATABASE"
        backup_disk_env = "OPEN_FNR_CLICKHOUSE_BACKUP_DISK"
    }
}

if ($Mode -eq "plan") {
    $plan | ConvertTo-Json -Depth 6
    exit 0
}

$postgresHost = Require-Env "OPEN_FNR_POSTGRES_HOST"
$postgresPort = Require-Env "OPEN_FNR_POSTGRES_PORT"
$postgresDatabase = Require-Env "OPEN_FNR_POSTGRES_DATABASE"
$postgresUser = Require-Env "OPEN_FNR_POSTGRES_USER"
$clickhouseHost = Require-Env "OPEN_FNR_CLICKHOUSE_HOST"
$clickhousePort = Require-Env "OPEN_FNR_CLICKHOUSE_HTTP_PORT"
$clickhouseDatabase = Require-Env "OPEN_FNR_CLICKHOUSE_DATABASE"
$clickhouseBackupDisk = Require-Env "OPEN_FNR_CLICKHOUSE_BACKUP_DISK"

New-Item -ItemType Directory -Force -Path $targetDir | Out-Null

$postgresDump = Join-Path $targetDir "postgres_open_fnr.dump"
& pg_dump --host $postgresHost --port $postgresPort --username $postgresUser --dbname $postgresDatabase --format custom --file $postgresDump

$clickhouseBackupName = "open_fnr_$timestamp"
& clickhouse-client --host $clickhouseHost --port $clickhousePort --query "BACKUP DATABASE $clickhouseDatabase TO Disk('$clickhouseBackupDisk', '$clickhouseBackupName')"

$manifestPath = Join-Path $targetDir "backup_manifest.json"
$manifest = [ordered]@{
    created_at = (Get-Date).ToUniversalTime().ToString("o")
    backup_root_env = "OPEN_FNR_BACKUP_ROOT_PATH"
    postgres_dump = $postgresDump
    postgres_sha256 = (Get-FileHash -Algorithm SHA256 -Path $postgresDump).Hash
    clickhouse_backup_name = $clickhouseBackupName
    clickhouse_database_env = "OPEN_FNR_CLICKHOUSE_DATABASE"
    clickhouse_backup_disk_env = "OPEN_FNR_CLICKHOUSE_BACKUP_DISK"
}
$manifest | ConvertTo-Json -Depth 5 | Set-Content -Encoding utf8 -Path $manifestPath
$manifest | ConvertTo-Json -Depth 5
