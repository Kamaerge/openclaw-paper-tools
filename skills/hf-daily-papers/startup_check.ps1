#!/usr/bin/env pwsh
<#
.SYNOPSIS
    OpenClaw 论文推送系统 - 开机启动检查脚本
.DESCRIPTION
    此脚本在系统启动时运行，确保 OpenClaw 和相关服务正常工作
#>

param(
    [switch]$Verbose
)

$ErrorActionPreference = 'Continue'

function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $color = switch ($Level) {
        "INFO" { "Cyan" }
        "SUCCESS" { "Green" }
        "WARNING" { "Yellow" }
        "ERROR" { "Red" }
        default { "White" }
    }
    Write-Host "[$timestamp] [$Level] $Message" -ForegroundColor $color
}

Write-Log "OpenClaw 论文推送系统 - 启动检查" "INFO"

# 1. 检查 OpenClaw 是否可用
Write-Log "检查 OpenClaw CLI..." "INFO"
try {
    $openclawVersion = openclaw --version 2>&1 | Out-String
    if ($LASTEXITCODE -eq 0) {
        Write-Log "OpenClaw 可用: $($openclawVersion.Trim())" "SUCCESS"
    } else {
        Write-Log "OpenClaw 命令执行异常" "WARNING"
    }
} catch {
    Write-Log "OpenClaw 未安装或不在 PATH 中: $_" "ERROR"
}

# 2. 检查 Python 环境
Write-Log "检查 Python 环境..." "INFO"
try {
    $pythonBin = if (Test-Path "C:\MiniConda\python.exe") {
        "C:\MiniConda\python.exe"
    } else {
        "python"
    }
    $pythonVersion = & $pythonBin --version 2>&1 | Out-String
    if ($LASTEXITCODE -eq 0) {
        Write-Log "Python 可用: $($pythonVersion.Trim())" "SUCCESS"
    } else {
        Write-Log "Python 命令执行异常" "WARNING"
    }
} catch {
    Write-Log "Python 未找到: $_" "ERROR"
}

# 3. 检查计划任务状态
Write-Log "检查计划任务..." "INFO"
try {
    $task = Get-ScheduledTask -TaskName "OpenClaw-HF-Daily-Papers-Feishu" -ErrorAction SilentlyContinue
    if ($task) {
        $info = Get-ScheduledTaskInfo -TaskName "OpenClaw-HF-Daily-Papers-Feishu"
        Write-Log "计划任务状态: $($task.State)" "SUCCESS"
        Write-Log "下次运行时间: $($info.NextRunTime)" "INFO"
        Write-Log "上次运行时间: $($info.LastRunTime)" "INFO"
        
        # 检查上次运行结果
        if ($info.LastTaskResult -eq 0) {
            Write-Log "上次运行成功" "SUCCESS"
        } elseif ($info.LastTaskResult -ne 0 -and $info.LastRunTime -ne $null) {
            Write-Log "上次运行失败 (代码: 0x$($info.LastTaskResult.ToString('X')))" "WARNING"
        }
    } else {
        Write-Log "计划任务未找到，需要注册" "WARNING"
    }
} catch {
    Write-Log "检查计划任务失败: $_" "ERROR"
}

# 4. 检查工作目录和文件
Write-Log "检查工作目录..." "INFO"
$workDir = "D:\Project\openclaw-paper-tools\skills\hf-daily-papers"
if (Test-Path $workDir) {
    Write-Log "工作目录存在: $workDir" "SUCCESS"
    
    $requiredFiles = @(
        "generator.py",
        "multi_source_fetcher.py",
        "run_and_send.ps1",
        "run_and_send_task.ps1"
    )
    
    foreach ($file in $requiredFiles) {
        $filePath = Join-Path $workDir $file
        if (Test-Path $filePath) {
            Write-Log "  ✓ $file" "SUCCESS"
        } else {
            Write-Log "  ✗ $file 缺失" "ERROR"
        }
    }
} else {
    Write-Log "工作目录不存在: $workDir" "ERROR"
}

# 5. 检查网络连接
Write-Log "检查网络连接..." "INFO"
try {
    $arxivTest = Test-NetConnection -ComputerName "arxiv.org" -Port 443 -InformationLevel Quiet -WarningAction SilentlyContinue
    if ($arxivTest) {
        Write-Log "arXiv 连接正常" "SUCCESS"
    } else {
        Write-Log "arXiv 连接失败" "WARNING"
    }
} catch {
    Write-Log "网络检查失败: $_" "WARNING"
}

Write-Log "启动检查完成" "SUCCESS"

# 可选：如果是第一次运行（今天还没推送），可以执行一次手动推送
if ($env:AUTO_RUN_ON_STARTUP -eq '1') {
    Write-Log "检测到 AUTO_RUN_ON_STARTUP=1，准备执行推送..." "INFO"
    $cacheFile = Join-Path $workDir "submitted_papers.json"
    $todayFile = Join-Path $workDir "recommendations\$(Get-Date -Format 'yyyy-MM-dd').md"
    
    if (-not (Test-Path $todayFile)) {
        Write-Log "今天还未推送，执行推送任务..." "INFO"
        try {
            Push-Location $workDir
            & "$workDir\run_and_send.ps1"
            Write-Log "推送任务执行完成" "SUCCESS"
        } catch {
            Write-Log "推送任务执行失败: $_" "ERROR"
        } finally {
            Pop-Location
        }
    } else {
        Write-Log "今天已经推送过论文，跳过" "INFO"
    }
}

Write-Log "所有检查完成，系统就绪" "SUCCESS"
