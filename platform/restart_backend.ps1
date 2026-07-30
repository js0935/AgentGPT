# 重啟 AgentGPT 後端服務
$venv = "C:\Users\JS\AppData\Local\pypoetry\Cache\virtualenvs\reworkd-platform-vQfEAOYy-py3.14"
$python = Join-Path $venv "Scripts\python.exe"
$workdir = "C:\Users\JS\Desktop\base\AgentGPT\platform"

# 殺掉所有佔用 port 3000 的 process
Get-NetTCPConnection -LocalPort 3000 -ErrorAction SilentlyContinue | ForEach-Object {
    Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue
}
Start-Sleep -Seconds 2

# 啟動後端
$env:PYTHONPATH = $workdir
Start-Process -NoNewWindow -FilePath $python -ArgumentList "-m", "reworkd_platform", "--host", "0.0.0.0", "--port", "3000" -WorkingDirectory $workdir

Write-Host "Backend started on port 3000"
