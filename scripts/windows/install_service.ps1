param(
  [string]$TaskName = $env:SERVICE_NAME
)
if (-not $TaskName) { $TaskName = "WhalezAIGateway" }

$root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$bat = Join-Path $root "scripts\windows\start_backend_service.bat"

$action = New-ScheduledTaskAction -Execute $bat
$trigger = New-ScheduledTaskTrigger -AtStartup
$settings = New-ScheduledTaskSettingsSet -RestartCount 3 -RestartInterval (New-TimeSpan -Minutes 1) -AllowStartIfOnBatteries
Register-ScheduledTask -TaskName $TaskName -Action $action -Trigger $trigger -Settings $settings -Description "Whalez-AI Gateway (Waitress)" -RunLevel Highest -Force
Write-Host "Installed service task: $TaskName"
