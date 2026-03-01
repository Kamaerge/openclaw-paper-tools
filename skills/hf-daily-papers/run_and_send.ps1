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

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$outDir = Join-Path $scriptDir 'recommendations'
$dateStr = Get-Date -Format 'yyyy-MM-dd'
$mdFile = Join-Path $outDir ("$dateStr.md")

$openclawBin = if ($env:OPENCLAW_BIN) { $env:OPENCLAW_BIN } else { 'openclaw' }
$pythonBin = if ($env:PYTHON_BIN) { $env:PYTHON_BIN } else { 'python' }
$openclawChannel = if ($env:OPENCLAW_CHANNEL) { $env:OPENCLAW_CHANNEL } else { 'feishu' }

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
    & $pythonBin (Join-Path $scriptDir 'generator.py') | Out-Null

    if (-not (Test-Path $mdFile)) {
        throw "Missing markdown output: $mdFile"
    }

    $lines = Get-Content -Path $mdFile -Encoding UTF8
    $genItems = New-Object System.Collections.Generic.List[object]
    $effItems = New-Object System.Collections.Generic.List[object]
    $cur = ''

    foreach ($line in $lines) {
        if ($line.StartsWith('## 🎨')) {
            $cur = 'gen'
            continue
        }
        if ($line.StartsWith('## ⚡')) {
            $cur = 'eff'
            continue
        }

        $m = [regex]::Match($line, '^### \[(\d+\.\d+)\]\(https://huggingface\.co/papers/\1\) - (.*)$')
        if ($m.Success -and $cur) {
            $paperId = $m.Groups[1].Value
            $title = $m.Groups[2].Value.Trim()
            $item = [PSCustomObject]@{ pid = $paperId; title = $title }
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
            [Parameter(Mandatory = $true)]
            [object[]]$Items,
            [System.Collections.Generic.HashSet[string]]$Seen,
            [int]$MaxN = 10
        )

        $out = New-Object System.Collections.Generic.List[string]
        foreach ($item in $Items) {
            if ($Seen.Contains($item.pid)) { continue }
            [void]$Seen.Add($item.pid)

            $title = ($item.title -replace '\s+', ' ').Trim()
            if ($title.Length -gt 90) {
                $title = $title.Substring(0, 87) + '...'
            }

            $out.Add("- $($item.pid) $title`n  https://huggingface.co/papers/$($item.pid)")
            if ($out.Count -ge $MaxN) { break }
        }

        if ($out.Count -eq 0) { return '- (none)' }
        return ($out -join "`n")
    }

    $genText = Format-Items -Items $genItems.ToArray() -Seen $seen -MaxN 10
    $effText = Format-Items -Items $effItems.ToArray() -Seen $seen -MaxN 10

    $msg = @"
HF Daily Papers ($dateStr)

Generation
$genText

Efficient
$effText

(auto)
"@

    & $openclawBin message send --channel $openclawChannel --target $openclawTarget --message $msg --silent | Out-Null
    Write-Host "Sent daily papers via channel '$openclawChannel' to target '$openclawTarget'."
}
finally {
    Pop-Location
}
