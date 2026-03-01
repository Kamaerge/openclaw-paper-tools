param(
    [Parameter(Mandatory = $true)]
    [string]$FeishuTarget,
    [string]$TaskName = 'OpenClaw-HF-Daily-Papers-Feishu',
    [string]$Time = '08:00',
    [string]$OpenclawChannel = 'feishu',
    [string]$OpenclawBin = 'openclaw',
    [string]$PythonBin = 'python'
)

$ErrorActionPreference = 'Stop'

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$runner = Join-Path $scriptDir 'run_and_send.ps1'
$taskCmd = Join-Path $scriptDir 'run_and_send_task.cmd'

if (-not (Test-Path $runner)) {
    throw "Missing runner script: $runner"
}

$cmdContent = @"
@echo off
set "OPENCLAW_CHANNEL=$OpenclawChannel"
set "OPENCLAW_TARGET=$FeishuTarget"
set "OPENCLAW_BIN=$OpenclawBin"
set "PYTHON_BIN=$PythonBin"
set "PYTHONUTF8=1"
set "PYTHONIOENCODING=utf-8"
pwsh -NoProfile -ExecutionPolicy Bypass -File "$runner"
"@

Set-Content -Path $taskCmd -Value $cmdContent -Encoding ASCII

$createArgs = @(
    '/Create',
    '/SC', 'DAILY',
    '/ST', $Time,
    '/TN', $TaskName,
    '/TR', ('"' + $taskCmd + '"'),
    '/F'
)

& schtasks.exe @createArgs | Out-Host

Write-Host "Task created: $TaskName at $Time"
Write-Host "Task runner: $taskCmd"
Write-Host "You can test now: schtasks /Run /TN \"$TaskName\""
