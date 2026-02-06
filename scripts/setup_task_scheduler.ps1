# PowerShell script to set up Windows Task Scheduler for daily arXiv fetch
# Run this script as Administrator

# Configuration
$TaskName = "ArxivGothicDailyFetch"
$Description = "Daily fetch of GenAI and Cybersecurity papers from arXiv with Grok analysis"
$ScriptPath = Join-Path $PSScriptRoot "run_daily_fetch.bat"
$ProjectPath = Split-Path $PSScriptRoot -Parent

# Check if running as Administrator
$currentPrincipal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
if (-not $currentPrincipal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Write-Host "ERROR: This script must be run as Administrator" -ForegroundColor Red
    Write-Host "Right-click PowerShell and select 'Run as Administrator'" -ForegroundColor Yellow
    exit 1
}

Write-Host "Setting up Windows Task Scheduler for Gothic arXiv..." -ForegroundColor Green
Write-Host "Project path: $ProjectPath" -ForegroundColor Cyan
Write-Host "Script path: $ScriptPath" -ForegroundColor Cyan

# Check if script exists
if (-not (Test-Path $ScriptPath)) {
    Write-Host "ERROR: Script not found at $ScriptPath" -ForegroundColor Red
    exit 1
}

# Delete existing task if it exists
$existingTask = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
if ($existingTask) {
    Write-Host "Removing existing task..." -ForegroundColor Yellow
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
}

# Create scheduled task action
$action = New-ScheduledTaskAction `
    -Execute "cmd.exe" `
    -Argument "/c `"$ScriptPath`"" `
    -WorkingDirectory $ProjectPath

# Create trigger (daily at 3:00 AM)
$trigger = New-ScheduledTaskTrigger `
    -Daily `
    -At "3:00AM"

# Create settings
$settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -RunOnlyIfNetworkAvailable `
    -ExecutionTimeLimit (New-TimeSpan -Hours 2)

# Create principal (run whether user is logged on or not)
$principal = New-ScheduledTaskPrincipal `
    -UserId $env:USERNAME `
    -LogonType S4U `
    -RunLevel Highest

# Register the task
Register-ScheduledTask `
    -TaskName $TaskName `
    -Description $Description `
    -Action $action `
    -Trigger $trigger `
    -Settings $settings `
    -Principal $principal

Write-Host ""
Write-Host "Task scheduled successfully!" -ForegroundColor Green
Write-Host "Task Name: $TaskName" -ForegroundColor Cyan
Write-Host "Schedule: Daily at 3:00 AM" -ForegroundColor Cyan
Write-Host ""
Write-Host "To verify, open Task Scheduler (taskschd.msc) and look for '$TaskName'" -ForegroundColor Yellow
Write-Host ""
Write-Host "To run the task manually:" -ForegroundColor Yellow
Write-Host "  Start-ScheduledTask -TaskName '$TaskName'" -ForegroundColor Cyan
Write-Host ""
Write-Host "To delete the task:" -ForegroundColor Yellow
Write-Host "  Unregister-ScheduledTask -TaskName '$TaskName' -Confirm:`$false" -ForegroundColor Cyan
