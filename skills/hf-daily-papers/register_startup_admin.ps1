#!/usr/bin/env pwsh
<#
.SYNOPSIS
    为 OpenClaw 论文推送系统配置开机自启动（管理员权限）
.DESCRIPTION
    此脚本需要管理员权限运行，将创建系统级别的开机启动任务
#>

param(
    [switch]$AutoRunOnStartup,
    [int]$DelayMinutes = 3
)

# 检查管理员权限
$isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "⚠️  此脚本需要管理员权限运行" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "请使用以下方式之一运行:" -ForegroundColor Cyan
    Write-Host "  1. 右键点击 PowerShell，选择 '以管理员身份运行'" -ForegroundColor White
    Write-Host "  2. 或者在当前窗口运行：" -ForegroundColor White
    Write-Host "     Start-Process pwsh -ArgumentList '-NoProfile -ExecutionPolicy Bypass -File `"$PSCommandPath`"' -Verb RunAs" -ForegroundColor Gray
    Write-Host ""
    
    $response = Read-Host "是否尝试自动提升权限？(Y/N)"
    if ($response -eq 'Y' -or $response -eq 'y') {
        $arguments = "-NoProfile -ExecutionPolicy Bypass -File `"$PSCommandPath`""
        if ($AutoRunOnStartup) {
            $arguments += " -AutoRunOnStartup"
        }
        $arguments += " -DelayMinutes $DelayMinutes"
        
        Start-Process pwsh -ArgumentList $arguments -Verb RunAs
        exit
    } else {
        exit 1
    }
}

$ErrorActionPreference = 'Stop'

Write-Host "=== 配置 OpenClaw 论文推送系统开机自启动（管理员模式）===" -ForegroundColor Green

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$startupScript = Join-Path $scriptDir "startup_check.ps1"

# 创建 wrapper 脚本
$wrapperScript = Join-Path $scriptDir "startup_task.ps1"
$wrapperContent = @"
# OpenClaw 论文推送系统 - 开机启动任务
`$env:AUTO_RUN_ON_STARTUP = "$([int]$AutoRunOnStartup.IsPresent)"

# 切换到脚本目录
Set-Location "$scriptDir"

# 执行启动检查
& "$startupScript" -Verbose

# 记录日志
`$logFile = Join-Path "$scriptDir" "startup_\$(Get-Date -Format 'yyyy-MM-dd').log"
"Startup task executed at \$(Get-Date)" | Out-File -Append -FilePath `$logFile
"@

Set-Content -Path $wrapperScript -Value $wrapperContent -Encoding UTF8
Write-Host "✓ 创建启动任务脚本: $wrapperScript" -ForegroundColor Green

# 删除已存在的任务
Write-Host "`n删除已存在的任务..." -ForegroundColor Yellow
schtasks /Delete /TN "OpenClaw-Papers-Startup" /F 2>$null | Out-Null

# 创建新任务
Write-Host "创建开机启动任务..." -ForegroundColor Yellow

$createResult = schtasks /Create `
    /TN "OpenClaw-Papers-Startup" `
    /TR "pwsh.exe -NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File `"$wrapperScript`"" `
    /SC ONSTART `
    /DELAY 0003:00 `
    /RL LIMITED `
    /F 2>&1

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ 开机自启动任务创建成功" -ForegroundColor Green
} else {
    Write-Host "❌ 任务创建失败:" -ForegroundColor Red
    Write-Host $createResult
    exit 1
}

Write-Host ""
Write-Host "任务详情:" -ForegroundColor Cyan
Write-Host "  • 任务名称: OpenClaw-Papers-Startup"
Write-Host "  • 触发时机: 系统启动后 $DelayMinutes 分钟"
Write-Host "  • 运行脚本: $wrapperScript"
Write-Host "  • 开机自动推送: $AutoRunOnStartup"
Write-Host ""

# 验证任务
Write-Host "验证任务..." -ForegroundColor Yellow
schtasks /Query /TN "OpenClaw-Papers-Startup" /FO TABLE

Write-Host ""
Write-Host "=== 配置完成 ===" -ForegroundColor Green
Write-Host ""
Write-Host "📋 已配置的计划任务:" -ForegroundColor Cyan
Write-Host "  1. OpenClaw-Papers-Startup (开机启动检查)"
Write-Host "  2. OpenClaw-HF-Daily-Papers-Feishu (每日 8:00 推送)"
Write-Host ""
Write-Host "🔍 管理命令:" -ForegroundColor Yellow
Write-Host "  查看状态: schtasks /Query /TN `"OpenClaw-Papers-Startup`""
Write-Host "  手动运行: schtasks /Run /TN `"OpenClaw-Papers-Startup`""
Write-Host "  禁用任务: schtasks /Change /TN `"OpenClaw-Papers-Startup`" /DISABLE"
Write-Host "  删除任务: schtasks /Delete /TN `"OpenClaw-Papers-Startup`" /F"
Write-Host ""

$testResponse = Read-Host "是否立即测试运行？(Y/N)"
if ($testResponse -eq 'Y' -or $testResponse -eq 'y') {
    Write-Host "`n开始测试..." -ForegroundColor Cyan
    & $wrapperScript
}
