# OpenClaw 论文推送系统 - 开机启动任务
$env:AUTO_RUN_ON_STARTUP = "0"

# 切换到脚本目录
Set-Location "D:\Project\openclaw-paper-tools\skills\hf-daily-papers"

# 执行启动检查
& "D:\Project\openclaw-paper-tools\skills\hf-daily-papers\startup_check.ps1" -Verbose

# 记录日志
$logFile = Join-Path "D:\Project\openclaw-paper-tools\skills\hf-daily-papers" "startup_\2026-03-02.log"
"Startup task executed at \03/02/2026 13:11:25" | Out-File -Append -FilePath $logFile
