$ErrorActionPreference = "Stop"

$services = @(
  @{ Name = "Airflow"; Url = "http://127.0.0.1:18088/health" },
  @{ Name = "ClickHouse"; Url = "http://127.0.0.1:18123/ping" },
  @{ Name = "Flowable"; Url = "http://127.0.0.1:18080/flowable-rest/service/management/engine"; Credential = "rest-admin:test" },
  @{ Name = "OpenSearch"; Url = "http://127.0.0.1:19200" },
  @{ Name = "Superset"; Url = "http://127.0.0.1:18089/health" }
)

Write-Host "OPEN FNR development service health"

foreach ($service in $services) {
  $headers = @{}
  if ($service.ContainsKey("Credential")) {
    $bytes = [System.Text.Encoding]::ASCII.GetBytes($service.Credential)
    $headers.Authorization = "Basic " + [Convert]::ToBase64String($bytes)
  }

  try {
    $response = Invoke-WebRequest -Uri $service.Url -Headers $headers -UseBasicParsing -TimeoutSec 5
    Write-Host ("OK   {0,-12} HTTP {1}" -f $service.Name, [int]$response.StatusCode)
  }
  catch {
    Write-Host ("FAIL {0,-12} {1}" -f $service.Name, $_.Exception.Message)
    exit 1
  }
}
