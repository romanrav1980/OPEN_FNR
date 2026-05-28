param(
    [Parameter(Mandatory = $true)]
    [string]$BusinessDate,

    [Parameter(Mandatory = $true)]
    [string]$LandingRootPath
)

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$env:PYTHONPATH = Join-Path $repoRoot "apps\backend"

python -m open_fnr_api.pilot_fixtures --business-date $BusinessDate --landing-root-path $LandingRootPath
