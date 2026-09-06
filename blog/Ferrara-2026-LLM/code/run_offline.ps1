# 在项目范围运行，无网络调用；记录命令与输出，失败立即停止。
$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new()
$OutputEncoding = [System.Text.UTF8Encoding]::new()
$env:PYTHONIOENCODING = 'utf-8'
$env:PYTHONDONTWRITEBYTECODE = '1'
$projectRoot = Split-Path -Parent $PSScriptRoot
$localPython = Join-Path $projectRoot '.venv/Scripts/python.exe'
if (Test-Path -LiteralPath $localPython) {
    $taskPython = $localPython
} elseif ($env:PYTHON_EXE -and (Test-Path -LiteralPath $env:PYTHON_EXE)) {
    $taskPython = $env:PYTHON_EXE
} else {
    throw '未找到项目 .venv 或有效 PYTHON_EXE；请配置可用的 Python。'
}
$env:MPLCONFIGDIR = Join-Path $projectRoot 'outputs/.mplconfig'
$taskLogs = Join-Path $projectRoot 'logs'
New-Item -ItemType Directory -Path $taskLogs -Force | Out-Null
$taskLog = Join-Path $taskLogs ('offline-run-' + (Get-Date -Format 'yyyyMMdd-HHmmss') + '.log')
& $taskPython --version 2>&1 | Tee-Object -FilePath $taskLog -Append
foreach ($script in @('01_check_inputs.py','02_prepare_annotation.py','03_evaluate.py',
                     'check_acceptance.py','04_make_figures.py')) {
    "RUN code/$script" | Tee-Object -FilePath $taskLog -Append
    & $taskPython (Join-Path $PSScriptRoot $script) 2>&1 |
        Tee-Object -FilePath $taskLog -Append
    if ($LASTEXITCODE -ne 0) {
        throw "code/$script 运行失败，退出码 $LASTEXITCODE。"
    }
}
"PASS: 离线执行完成；日志 $taskLog" | Tee-Object -FilePath $taskLog -Append
