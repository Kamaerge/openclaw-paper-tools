#!/usr/bin/env pwsh
<#
.SYNOPSIS
    配置 OpenClaw 论文推送系统开机自启动（用户级别，无需管理员权限）
.DESCRIPTION
    通过 Windows 启动文件夹配置开机自启动，只需当前用户权限
#>

param(
    [switch]$Remove
)

$ErrorActionPreference = 'Stop'

# 获取启动文件夹路径
$startupFolder = [Environment]::GetFolderPath('Startup')
$shortcutPath = Join-Path $startupFolder "OpenClaw-Papers-Startup.lnk"

if ($Remove) {
    Write-Host "=== 移除开机自启动配置 ===" -ForegroundColor Cyan
    if (Test-Path $shortcutPath) {
        Remove-Item $shortcutPath -Force
        Write-Host "✅ 已移除启动快捷方式" -ForegroundColor Green
    } else {
        Write-Host "⚠️  启动快捷方式不存在" -ForegroundColor Yellow
    }
    exit 0
}

Write-Host "=== 配置 OpenClaw 论文推送系统开机自启动（用户级别）===" -ForegroundColor Cyan

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$wrapperScript = Join-Path $scriptDir "startup_task.ps1"

# 确保 wrapper 脚本存在
if (-not (Test-Path $wrapperScript)) {
    Write-Host "创建启动脚本..." -ForegroundColor Yellow
    $startupCheckScript = Join-Path $scriptDir "startup_check.ps1"
    $wrapperContent = @"
# OpenClaw 论文推送系统 - 开机启动任务 (用户级别)
Set-Location "$scriptDir"

# 延迟3分钟，等待系统稳定
Start-Sleep -Seconds 180

# 执行启动检查
& "$startupCheckScript" -Verbose

# 记录日志
`$logFile = Join-Path "$scriptDir" "startup_\$(Get-Date -Format 'yyyy-MM-dd').log"
"[User Level] Startup task executed at \$(Get-Date)" | Out-File -Append -FilePath `$logFile
"@
    Set-Content -Path $wrapperScript -Value $wrapperContent -Encoding UTF8
}

# 创建快捷方式
Write-Host "创建启动快捷方式..." -ForegroundColor Yellow

$WScriptShell = New-Object -ComObject WScript.Shell
$Shortcut = $WScriptShell.CreateShortcut($shortcutPath)
$Shortcut.TargetPath = "pwsh.exe"
$Shortcut.Arguments = "-NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File `"$wrapperScript`""
$Shortcut.WorkingDirectory = $scriptDir
$Shortcut.Description = "OpenClaw 论文推送系统开机启动"
$Shortcut.Save()

Write-Host "✅ 开机自启动配置成功" -ForegroundColor Green
Write-Host ""
Write-Host "配置详情:" -ForegroundColor Cyan
Write-Host "  • 启动方式: Windows 启动文件夹"
Write-Host "  • 快捷方式: $shortcutPath"
Write-Host "  • 运行脚本: $wrapperScript"
Write-Host "  • 延迟时间: 3 分钟（脚本内置）"
Write-Host "  • 权限级别: 用户级别（无需管理员）"
Write-Host ""
Write-Host "📋 已配置的自启动:" -ForegroundColor Cyan
Write-Host "  1. OpenClaw-Papers-Startup (Windows 启动文件夹)"
Write-Host "  2. OpenClaw-HF-Daily-Papers-Feishu (每日 8:00 计划任务)"
Write-Host ""
Write-Host "🔍 管理命令:" -ForegroundColor Yellow
Write-Host "  查看快捷方式: explorer '$startupFolder'"
Write-Host "  手动测试: & '$wrapperScript'"
Write-Host "  删除自启动: .\register_startup_user.ps1 -Remove"
Write-Host ""

$testResponse = Read-Host "是否立即测试运行？(Y/N)"
if ($testResponse -eq 'Y' -or $testResponse -eq 'y') {
    Write-Host "`n开始测试（跳过延迟）..." -ForegroundColor Cyan
    $startupCheckScript = Join-Path $scriptDir "startup_check.ps1"
    & $startupCheckScript -Verbose
}
