# 从脚本所在目录启动，避免本机 profile.do 改变工作目录。
$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new()
if (-not $env:STATA_EXE -or -not (Test-Path -LiteralPath $env:STATA_EXE)) {
    throw 'STATA_EXE must point to an existing Stata 19 executable.'
}
$projectRoot = $PSScriptRoot
$logDir = Join-Path $projectRoot '05-logs'
New-Item -ItemType Directory -Path $logDir -Force | Out-Null
$stataRoot = $projectRoot.Replace('\', '/')
$entry = Join-Path $logDir 'launcher.do'
# 动态生成路径；分析仍由 master.do 统一执行。
$content = "cd `"$stataRoot`"`r`ndo `"master.do`"`r`n"
[IO.File]::WriteAllText($entry, $content, [Text.UTF8Encoding]::new($false))
$started = Get-Date
$process = Start-Process -FilePath $env:STATA_EXE `
    -ArgumentList ('/e do "' + $entry + '"') `
    -WorkingDirectory $projectRoot -WindowStyle Hidden -PassThru
$process.WaitForExit()
# Stata 的进程退出码不足以证明分析成功，继续检查日志与产物。
$runLog = Join-Path $logDir 'run.log'
if (-not (Test-Path -LiteralPath $runLog)) { throw 'run.log missing.' }
if ((Get-Item -LiteralPath $runLog).LastWriteTime -lt $started) {
    throw 'run.log was not updated.'
}
$text = Get-Content -LiteralPath $runLog -Raw -Encoding utf8
if ($text -match '(?m)^r\([0-9]+\);' -or $text -notmatch 'closed on:') {
    throw 'Stata did not complete. Inspect 05-logs/run.log.'
}
$figure = Join-Path $projectRoot '02-figs/publish/fig1_coef.png'
if (-not (Test-Path -LiteralPath $figure)) { throw 'Coefficient figure missing.' }
Write-Output 'Completed: 05-logs/run.log and 02-figs/publish/fig1_coef.png'
