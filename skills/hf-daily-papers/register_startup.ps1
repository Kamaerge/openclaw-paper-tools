#!/usr/bin/env pwsh
<#
.SYNOPSIS
    注册 OpenClaw 论文推送系统的开机自启动
.DESCRIPTION
    此脚本将创建 Windows 计划任务，在系统启动时自动运行启动检查脚本
.PARAMETER AutoRunOnStartup
    是否在开机时自动执行论文推送（如果今天还没推送）
.PARAMETER DelayMinutes
    开机后延迟多少分钟执行（默认5分钟，等待网络稳定）
#>

param(
    [switch]$AutoRunOnStartup,
    [int]$DelayMinutes = 5
)

$ErrorActionPreference = 'Stop'

Write-Host "=== 配置 OpenClaw 论文推送系统开机自启动 ===" -ForegroundColor Cyan

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$startupScript = Join-Path $scriptDir "startup_check.ps1"

if (-not (Test-Path $startupScript)) {
    throw "启动脚本不存在: $startupScript"
}

# 创建启动任务的 wrapper 脚本
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

# 使用 PowerShell 注册开机启动任务
$taskName = "OpenClaw-Papers-Startup"
$description = "OpenClaw 论文推送系统开机启动检查"

Write-Host "`n创建计划任务..." -ForegroundColor Yellow

try {
    # 创建触发器：系统启动后延迟指定分钟
    $trigger = New-ScheduledTaskTrigger -AtStartup
    $trigger.Delay = "PT$($DelayMinutes)M"  # ISO 8601 duration format
    
    # 创建操作
    $action = New-ScheduledTaskAction `
        -Execute "pwsh.exe" `
        -Argument "-NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File `"$wrapperScript`""
    
    # 创建设置
    $settings = New-ScheduledTaskSettingsSet `
        -AllowStartIfOnBatteries `
        -DontStopIfGoingOnBatteries `
        -StartWhenAvailable `
        -RunOnlyIfNetworkAvailable `
        -ExecutionTimeLimit (New-TimeSpan -Minutes 10)
    
    # 创建主体（使用当前用户）
    $principal = New-ScheduledTaskPrincipal `
        -UserId $env:USERNAME `
        -LogonType Interactive `
        -RunLevel Limited
    
    # 删除已存在的任务
    Unregister-ScheduledTask -TaskName $taskName -Confirm:$false -ErrorAction SilentlyContinue
    
    # 注册新任务
    Register-ScheduledTask `
        -TaskName $taskName `
        -Description $description `
        -Action $action `
        -Trigger $trigger `
        -Settings $settings `
        -Principal $principal | Out-Null
    
    Write-Host "✅ 开机自启动任务已创建: $taskName" -ForegroundColor Green
    Write-Host ""
    Write-Host "任务详情:" -ForegroundColor Cyan
    Write-Host "  • 任务名称: $taskName"
    Write-Host "  • 触发时机: 系统启动后 $DelayMinutes 分钟"
    Write-Host "  • 运行脚本: $wrapperScript"
    Write-Host "  • 网络要求: 需要网络连接"
    Write-Host "  • 开机自动推送: $($AutoRunOnStartup.IsPresent)"
    Write-Host ""
    
    # 测试运行
    Write-Host "🧪 是否立即测试运行？(Y/N)" -ForegroundColor Yellow
    $response = Read-Host
    if ($response -eq 'Y' -or $response -eq 'y') {
        Write-Host "`n开始测试运行..." -ForegroundColor Cyan
        & $wrapperScript
    }
    
} catch {
    Write-Host "❌ 创建开机启动任务失败: $_" -ForegroundColor Red
    throw
}

Write-Host "`n=== 配置完成 ===" -ForegroundColor Green
Write-Host ""
Write-Host "📋 已配置的计划任务:" -ForegroundColor Cyan
Write-Host "  1. OpenClaw-Papers-Startup (开机启动检查)"
Write-Host "  2. OpenClaw-HF-Daily-Papers-Feishu (每日 8:00 推送)"
Write-Host ""
Write-Host "🔍 管理命令:" -ForegroundColor Yellow
Write-Host "  查看状态: Get-ScheduledTask -TaskName 'OpenClaw-*' | Format-Table"
Write-Host "  手动运行: schtasks /Run /TN `"OpenClaw-Papers-Startup`""
Write-Host "  禁用任务: Disable-ScheduledTask -TaskName 'OpenClaw-Papers-Startup'"
Write-Host "  删除任务: Unregister-ScheduledTask -TaskName 'OpenClaw-Papers-Startup' -Confirm:`$false"
Write-Host ""
