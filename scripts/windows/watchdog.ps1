param(
  [string]$Url = "http://127.0.0.1:$env:SERVICE_PORT/api/health",
  [int]$Interval = [int]($env:HEALTHCHECK_INTERVAL_SEC ? $env:HEALTHCHECK_INTERVAL_SEC : 20),
  [int]$MaxFailures = [int]($env:HEALTHCHECK_RESTART_THRESHOLD ? $env:HEALTHCHECK_RESTART_THRESHOLD : 3),
  [string]$TaskName = ($env:SERVICE_NAME ? $env:SERVICE_NAME : "WhalezAIGateway")
)
$fail = 0
while ($true) {
  try {
    $resp = Invoke-WebRequest -UseBasicParsing -Uri $Url -TimeoutSec 6
    if ($resp.StatusCode -eq 200) { $fail = 0 }
    else { $fail++ }
  } catch { $fail++ }
  if ($fail -ge $MaxFailures) {
    Write-Host "[watchdog] restarting task $TaskName"
    Restart-ScheduledTask -TaskName $TaskName
    $fail = 0
  }
  Start-Sleep -Seconds $Interval
}
