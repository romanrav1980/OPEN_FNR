param(
    [Parameter(Mandatory = $true)]
    [string]$BusinessDate,

    [string]$LandingRootPath = ""
)

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$env:PYTHONPATH = Join-Path $repoRoot "apps\backend"

if ($LandingRootPath -eq "") {
    python -m open_fnr_api.shadow_load --business-date $BusinessDate
} else {
    python -m open_fnr_api.shadow_load --business-date $BusinessDate --landing-root-path $LandingRootPath
}
