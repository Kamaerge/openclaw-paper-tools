$ErrorActionPreference = 'Stop'

# Generate today's HF papers markdown, then send a compact list via OpenClaw messaging.
#
# Required env (Feishu first):
#   FEISHU_TARGET     e.g. chat_id/open_id/user_id per your OpenClaw channel adapter
# Optional compatibility env:
#   OPENCLAW_CHANNEL  default: feishu
#   OPENCLAW_TARGET   if set, overrides FEISHU_TARGET/TELEGRAM_TARGET
#   TELEGRAM_TARGET   backward compatibility only
# Optional env:
#   OPENCLAW_BIN      default: openclaw
#   PYTHON_BIN        default: python
#   HF_DAILY_PAPERS_PROXY  e.g. http://127.0.0.1:7897
#   HF_DAILY_INTERESTS      default: generation,efficient (可选: generation, efficient)
#   AUTO_SUBMIT_TOPN        default: 0 (设置 >0 后会自动提交 TopN 到 paper-submitter)
#   SUBMITTER_SCRIPT        default: ../paper-submitter/submitter.py

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$outDir = Join-Path $scriptDir 'recommendations'
$dateStr = Get-Date -Format 'yyyy-MM-dd'
$mdFile = Join-Path $outDir ("$dateStr.md")

$openclawBin = if ($env:OPENCLAW_BIN) { $env:OPENCLAW_BIN } else { 'openclaw' }

# Python 路径解析：优先使用 conda，其次使用 PYTHON_BIN 环境变量
$pythonBin = $null
if ($env:PYTHON_BIN -and (Test-Path $env:PYTHON_BIN)) {
    $pythonBin = $env:PYTHON_BIN
} else {
    # 尝试从常见位置找 conda Python
    $condaCandidates = 'C:\MiniConda\python.exe', 'C:\Anaconda3\python.exe', 'C:\conda\python.exe'
    foreach ($candidate in $condaCandidates) {
        if (Test-Path $candidate) {
            $pythonBin = $candidate
            break
        }
    }
}

# 如果仍未找到，使用 'python' 命令
if (-not $pythonBin) {
    $pythonBin = 'python'
}
$openclawChannel = if ($env:OPENCLAW_CHANNEL) { $env:OPENCLAW_CHANNEL } else { 'feishu' }
$interestRaw = if ($env:HF_DAILY_INTERESTS) { $env:HF_DAILY_INTERESTS } else { 'generation,efficient' }
$autoSubmitTopN = 0
if ($env:AUTO_SUBMIT_TOPN) {
    [void][int]::TryParse($env:AUTO_SUBMIT_TOPN, [ref]$autoSubmitTopN)
}
$submitterScript = if ($env:SUBMITTER_SCRIPT) {
    $env:SUBMITTER_SCRIPT
} else {
    Join-Path $scriptDir '..\paper-submitter\submitter.py'
}

$openclawTarget = $env:OPENCLAW_TARGET
if (-not $openclawTarget) { $openclawTarget = $env:FEISHU_TARGET }
if (-not $openclawTarget) { $openclawTarget = $env:TELEGRAM_TARGET }

if (-not $openclawTarget) {
    throw 'Missing target env. Set OPENCLAW_TARGET or FEISHU_TARGET.'
}

if ($env:HF_DAILY_PAPERS_PROXY) {
    $env:HTTP_PROXY = $env:HF_DAILY_PAPERS_PROXY
    $env:HTTPS_PROXY = $env:HF_DAILY_PAPERS_PROXY
}

$env:PYTHONUTF8 = '1'
$env:PYTHONIOENCODING = 'utf-8'

Push-Location $scriptDir
try {
    # 设置环境变量以确保传递给Python
    $env:PYTHONUTF8 = '1'
    
    & "$pythonBin" (Join-Path $scriptDir 'generator.py') | Out-Null

    if (-not (Test-Path $mdFile)) {
        throw "Missing markdown output: $mdFile"
    }

    $lines = Get-Content -Path $mdFile -Encoding UTF8
    $genItems = New-Object System.Collections.Generic.List[object]
    $effItems = New-Object System.Collections.Generic.List[object]
    $cur = ''

    foreach ($line in $lines) {
        if ($line.StartsWith('## 📌') -or $line.StartsWith('## 🎨')) {
            $cur = 'gen'
            continue
        }
        if ($line.StartsWith('## 📎') -or $line.StartsWith('## ⚡')) {
            $cur = 'eff'
            continue
        }

        # 支持多源格式：HuggingFace、arXiv 等
        $m = [regex]::Match($line, '^\s*### \[([^\]]+)\]\((https://[^\)]+)\) - (.*)$')
        if ($m.Success -and $cur) {
            $paperId = $m.Groups[1].Value
            $url = $m.Groups[2].Value        # 保留完整URL
            $titleAndSource = $m.Groups[3].Value.Trim()
            # 移除源标注（如 `arXiv (cs.CV)`）
            if ($titleAndSource -match '(.+?)\s+`[^`]+`$') {
                $title = $matches[1]
            } else {
                $title = $titleAndSource
            }
            $item = [PSCustomObject]@{ pid = $paperId; title = $title; url = $url }
            if ($cur -eq 'gen') {
                $genItems.Add($item)
            } else {
                $effItems.Add($item)
            }
        }
    }

    $seen = New-Object System.Collections.Generic.HashSet[string]

    function Format-Items {
        param(
            [Parameter(Mandatory = $false)]
            [object[]]$Items = @(),
            [System.Collections.Generic.HashSet[string]]$Seen,
            [int]$MaxN = 10
        )

        if (-not $Items -or $Items.Count -eq 0) {
            return '- (none)'
        }

        $out = New-Object System.Collections.Generic.List[string]
        foreach ($item in $Items) {
            if ($Seen.Contains($item.pid)) { continue }
            [void]$Seen.Add($item.pid)

            $title = ($item.title -replace '\s+', ' ').Trim()
            if ($title.Length -gt 90) {
                $title = $title.Substring(0, 87) + '...'
            }
            
            # 使用保存的URL，而不是硬编码HuggingFace链接
            $itemUrl = if ($item.url) { $item.url } else { "https://huggingface.co/papers/$($item.pid)" }
            $out.Add("- $($item.pid) $title`n  $itemUrl")
            if ($out.Count -ge $MaxN) { break }
        }

        if ($out.Count -eq 0) { return '- (none)' }
        return ($out -join "`n")
    }

    $genArray = if ($genItems -and $genItems.Count -gt 0) { $genItems.ToArray() } else { @() }
    $effArray = if ($effItems -and $effItems.Count -gt 0) { $effItems.ToArray() } else { @() }
    
    # 如果没有任何新论文，跳过发送消息
    if ($genArray.Count -eq 0 -and $effArray.Count -eq 0) {
        Write-Host "⚠️ No new papers found. Skipping message send." -ForegroundColor Yellow
        return
    }
    
    $genText = Format-Items -Items $genArray -Seen $seen -MaxN 10
    $effText = Format-Items -Items $effArray -Seen $seen -MaxN 10
    
    # 为输出添加来源标签
    $sourceTag = 'Multi-Source (HF + arXiv + PwC)'
    if ($genItems.Count -gt 0) {
        if ($genItems[0].url -like '*arxiv*') {
            $sourceTag = 'arXiv (Domain-Specific: CS.CV, CS.HC, CS.RO, CS.LG, STAT.ML)'
        } elseif ($genItems[0].url -like '*huggingface*') {
            $sourceTag = 'HuggingFace Papers'
        }
    }

    $interestSet = New-Object System.Collections.Generic.HashSet[string]
    foreach ($token in ($interestRaw -split ',')) {
        $name = $token.Trim().ToLower()
        if ($name) { [void]$interestSet.Add($name) }
    }
    if ($interestSet.Count -eq 0) {
        [void]$interestSet.Add('generation')
        [void]$interestSet.Add('efficient')
    }

    $messageSections = New-Object System.Collections.Generic.List[string]
    if ($interestSet.Contains('generation')) {
        $messageSections.Add("Generation`n$genText")
    }
    if ($interestSet.Contains('efficient')) {
        $messageSections.Add("Efficient`n$effText")
    }

    if ($messageSections.Count -eq 0) {
        $messageSections.Add("Generation`n$genText")
        $messageSections.Add("Efficient`n$effText")
    }

    $sectionsText = $messageSections -join "`n`n"

    $msg = @"
📰 Daily Papers Report ($dateStr)
📌 Source: $sourceTag

$sectionsText

---
(auto-generated by OpenClaw Paper Tools)
"@

    & $openclawBin message send --channel $openclawChannel --target $openclawTarget --message $msg --silent | Out-Null
    Write-Host "Sent daily papers via channel '$openclawChannel' to target '$openclawTarget'."

    if ($autoSubmitTopN -gt 0) {
        $useNanoPdfAnalyzer = $env:USE_NANOPDF_ANALYZER -eq '1'
        $useArxivAnalyzer = $env:USE_ARXIV_ANALYZER -eq '1'
        
        # 直接指定分析器脚本路径
        $paperSubmitterDir = Join-Path $scriptDir '..\paper-submitter'
        $analyzerScript = if ($useNanoPdfAnalyzer) {
            Join-Path $paperSubmitterDir 'analyze_with_nanopdf.py'
        } else {
            # 默认使用 nano-pdf 分析器
            Join-Path $paperSubmitterDir 'analyze_with_nanopdf.py'
        }
        
        if (-not (Test-Path $analyzerScript)) {
            throw "AUTO_SUBMIT_TOPN is set, but analyzer script was not found: $analyzerScript"
        }

        $toSubmit = New-Object System.Collections.Generic.List[string]
        $submitSeen = New-Object System.Collections.Generic.HashSet[string]

        if ($interestSet.Contains('generation')) {
            foreach ($item in $genItems) {
                if ($submitSeen.Add($item.pid)) { $toSubmit.Add($item.pid) }
                if ($toSubmit.Count -ge $autoSubmitTopN) { break }
            }
        }
        if ($toSubmit.Count -lt $autoSubmitTopN -and $interestSet.Contains('efficient')) {
            foreach ($item in $effItems) {
                if ($submitSeen.Add($item.pid)) { $toSubmit.Add($item.pid) }
                if ($toSubmit.Count -ge $autoSubmitTopN) { break }
            }
        }

        $analyzerName = if ($useNanoPdfAnalyzer) { "nano-pdf Analyzer" } elseif ($useArxivAnalyzer) { "arXiv Analyzer" } else { "SwiftScholar" }
        Write-Host "Auto submit enabled. Submitting $($toSubmit.Count) paper(s) to ${analyzerName}..."
        foreach ($paperId in $toSubmit) {
            Write-Host "  -> submit $paperId"
            # 使用最简单的直接调用方式
            & "$pythonBin" "$analyzerScript" "$paperId"
            if ($LASTEXITCODE -ne 0) {
                Write-Warning "Analyzer failed for $paperId (exit code $LASTEXITCODE)."
            }
        }
    }
}
finally {
    Pop-Location
}
