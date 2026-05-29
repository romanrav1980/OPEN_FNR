param(
    [ValidateSet("plan", "execute")]
    [string]$Mode = "plan",
    [string]$ManifestPath = ""
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

$plan = [ordered]@{
    mode = $Mode
    purpose = "Restore smoke into dedicated restore databases only."
    manifest_path = $ManifestPath
    safety = @(
        "Default mode is plan.",
        "Execute mode requires a backup manifest.",
        "Execute mode requires dedicated OPEN_FNR_RESTORE_POSTGRES_DATABASE and OPEN_FNR_RESTORE_CLICKHOUSE_DATABASE values."
    )
    required_env_for_execute = @(
        "OPEN_FNR_POSTGRES_HOST",
        "OPEN_FNR_POSTGRES_PORT",
        "OPEN_FNR_POSTGRES_USER",
        "OPEN_FNR_RESTORE_POSTGRES_DATABASE",
        "OPEN_FNR_CLICKHOUSE_HOST",
        "OPEN_FNR_CLICKHOUSE_HTTP_PORT",
        "OPEN_FNR_RESTORE_CLICKHOUSE_DATABASE"
    )
}

if ($Mode -eq "plan") {
    $plan | ConvertTo-Json -Depth 5
    exit 0
}

if ([string]::IsNullOrWhiteSpace($ManifestPath)) {
    throw "ManifestPath is required in execute mode."
}

$postgresHost = Require-Env "OPEN_FNR_POSTGRES_HOST"
$postgresPort = Require-Env "OPEN_FNR_POSTGRES_PORT"
$postgresUser = Require-Env "OPEN_FNR_POSTGRES_USER"
$restorePostgresDatabase = Require-Env "OPEN_FNR_RESTORE_POSTGRES_DATABASE"
$clickhouseHost = Require-Env "OPEN_FNR_CLICKHOUSE_HOST"
$clickhousePort = Require-Env "OPEN_FNR_CLICKHOUSE_HTTP_PORT"
$restoreClickhouseDatabase = Require-Env "OPEN_FNR_RESTORE_CLICKHOUSE_DATABASE"

$manifest = Get-Content -Raw -Path $ManifestPath | ConvertFrom-Json
if (-not (Test-Path $manifest.postgres_dump)) {
    throw "PostgreSQL dump from manifest was not found."
}

$actualHash = (Get-FileHash -Algorithm SHA256 -Path $manifest.postgres_dump).Hash
if ($actualHash -ne $manifest.postgres_sha256) {
    throw "PostgreSQL dump checksum does not match manifest."
}

& pg_restore --host $postgresHost --port $postgresPort --username $postgresUser --dbname $restorePostgresDatabase --exit-on-error $manifest.postgres_dump
& clickhouse-client --host $clickhouseHost --port $clickhousePort --query "CREATE DATABASE IF NOT EXISTS $restoreClickhouseDatabase"

[ordered]@{
    restored_at = (Get-Date).ToUniversalTime().ToString("o")
    manifest_path = $ManifestPath
    postgres_restore_database_env = "OPEN_FNR_RESTORE_POSTGRES_DATABASE"
    clickhouse_restore_database_env = "OPEN_FNR_RESTORE_CLICKHOUSE_DATABASE"
    postgres_checksum_verified = $true
} | ConvertTo-Json -Depth 5
