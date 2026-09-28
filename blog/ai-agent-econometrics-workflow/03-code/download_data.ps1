# 仅在 Stata webuse 连接失败时使用同一官方地址下载快照。
$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
$target = Join-Path $projectRoot '04-data/nlswork.dta'
if (Test-Path -LiteralPath $target) {
    Write-Output 'Local snapshot exists; download skipped.'
    return
}
New-Item -ItemType Directory -Path (Split-Path -Parent $target) -Force |
    Out-Null
Invoke-WebRequest -Uri 'https://www.stata-press.com/data/r19/nlswork.dta' `
    -OutFile $target
Get-FileHash -LiteralPath $target -Algorithm SHA256
