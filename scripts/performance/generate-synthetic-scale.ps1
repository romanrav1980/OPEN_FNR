param(
  [int]$Stores = 3000,
  [int]$SkusPerStore = 5500,
  [int]$HorizonDays = 30,
  [int]$ShardCount = 8
)

$activePairs = $Stores * $SkusPerStore
$forecastRows = $activePairs * $HorizonDays

[PSCustomObject]@{
  stores = $Stores
  skus_per_store = $SkusPerStore
  horizon_days = $HorizonDays
  active_pairs = $activePairs
  forecast_rows = $forecastRows
  shard_count = $ShardCount
  rows_per_shard = [math]::Ceiling($forecastRows / $ShardCount)
} | ConvertTo-Json
