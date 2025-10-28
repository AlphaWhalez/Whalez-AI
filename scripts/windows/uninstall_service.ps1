param([string]$TaskName = $env:SERVICE_NAME)
if (-not $TaskName) { $TaskName = "WhalezAIGateway" }
Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
Write-Host "Removed service task: $TaskName"
