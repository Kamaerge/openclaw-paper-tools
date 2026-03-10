param(
    [Parameter(Mandatory = $true)]
    [string]$FeishuTarget,
    [string]$TaskName = 'OpenClaw-HF-Daily-Papers-Feishu',
    [string]$Time = '08:00',
    [string]$OpenclawChannel = 'feishu',
    [string]$OpenclawBin = 'openclaw',
    [string]$PythonBin = 'python',
    [string]$InterestDomains = 'generation,efficient',
    [string]$GenKeywords = '',
    [string]$EffKeywords = '',
    [int]$AutoSubmitTopN = 10,
    [switch]$UseNanoPdfAnalyzer,
    [switch]$UseArxivAnalyzer,
    [switch]$UseMultiSource,  # 移除默认值，后面用条件处理
    [string]$NotionApiKey = '',
    [string]$NotionPapersDbId = ''
)

$ErrorActionPreference = 'Stop'

# 处理 UseMultiSource 默认值（如果未指定则为 $true）
if (-not $PSBoundParameters.ContainsKey('UseMultiSource')) {
    $UseMultiSource = $true
}

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$runner = Join-Path $scriptDir 'run_and_send.ps1'
$taskScript = Join-Path $scriptDir 'run_and_send_task.ps1'

if (-not (Test-Path $runner)) {
    throw "Missing runner script: $runner"
}

# 生成 PowerShell 脚本（不是 .cmd），这样环境变量能被正确继承
$scriptLines = @()
$scriptLines += "`$env:OPENCLAW_CHANNEL = `"$OpenclawChannel`""
$scriptLines += "`$env:OPENCLAW_TARGET = `"$FeishuTarget`""
$scriptLines += "`$env:OPENCLAW_BIN = `"$OpenclawBin`""
$scriptLines += "`$env:PYTHON_BIN = `"$PythonBin`""
$scriptLines += "`$env:HF_DAILY_INTERESTS = `"$InterestDomains`""

if ($GenKeywords) {
    $scriptLines += "`$env:HF_DAILY_GEN_KEYWORDS = `"$GenKeywords`""
}
if ($EffKeywords) {
    $scriptLines += "`$env:HF_DAILY_EFF_KEYWORDS = `"$EffKeywords`""
}

$scriptLines += "`$env:AUTO_SUBMIT_TOPN = `"$AutoSubmitTopN`""

if ($UseMultiSource) {
    $scriptLines += "`$env:USE_MULTI_SOURCE = `"1`""
} else {
    $scriptLines += "`$env:USE_MULTI_SOURCE = `"0`""
}

if ($UseNanoPdfAnalyzer) {
    $scriptLines += "`$env:USE_NANOPDF_ANALYZER = `"1`""
} elseif ($UseArxivAnalyzer) {
    $scriptLines += "`$env:USE_ARXIV_ANALYZER = `"1`""
}

$scriptLines += "`$env:PYTHONUTF8 = `"1`""
$scriptLines += "`$env:PYTHONIOENCODING = `"utf-8`""

if ($NotionApiKey) {
    $scriptLines += "`$env:NOTION_API_KEY = `"$NotionApiKey`""
}
if ($NotionPapersDbId) {
    $scriptLines += "`$env:NOTION_PAPERS_DB_ID = `"$NotionPapersDbId`""
}

if ($env:HF_DAILY_PAPERS_PROXY) {
    $scriptLines += "`$env:HF_DAILY_PAPERS_PROXY = `"$($env:HF_DAILY_PAPERS_PROXY)`""
}

$scriptLines += ''
$scriptLines += "& `"$runner`""

$scriptContent = $scriptLines -join "`r`n"
Set-Content -Path $taskScript -Value $scriptContent -Encoding UTF8

# 使用 PowerShell 注册计划任务（支持更多设置选项）
$action = New-ScheduledTaskAction -Execute "pwsh" -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$taskScript`""
$trigger = New-ScheduledTaskTrigger -Daily -At $Time
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable
$principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive

# 注册任务（如果存在则覆盖）
Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false -ErrorAction SilentlyContinue
Register-ScheduledTask -TaskName $TaskName -Action $action -Trigger $trigger -Settings $settings -Principal $principal | Out-Null

Write-Host "✅ Task created: $TaskName at $Time" -ForegroundColor Green
Write-Host "📝 Task runner: $taskScript"
Write-Host "⚡ 电池模式: 允许运行" -ForegroundColor Green
Write-Host "🧪 测试运行: schtasks /Run /TN `"$TaskName`"" -ForegroundColor Yellow
