# 一鍵啟動 AgentGPT（後端 3000 + 前端 3001）
# 用法: powershell -NoProfile -ExecutionPolicy Bypass -File start_all.ps1

Write-Host "=== AgentGPT 啟動器 ==="

# --- 資料庫 (MariaDB port 3307) ---
$db = Get-NetTCPConnection -LocalPort 3307 -State Listen -ErrorAction SilentlyContinue
if ($db) {
    Write-Host "[資料庫] Port 3307 已在運行 (PID $($db.OwningProcess))，跳過"
} else {
    Write-Host "[資料庫] MariaDB 啟動中..."
    & 'C:\Users\JS\Desktop\base\AgentGPT\start_mariadb.ps1'
    Start-Sleep -Seconds 6
}

# --- 後端 (port 3000) ---
$be = Get-NetTCPConnection -LocalPort 3000 -State Listen -ErrorAction SilentlyContinue
if ($be) {
    Write-Host "[後端] Port 3000 已在運行 (PID $($be.OwningProcess))，跳過"
} else {
    Write-Host "[後端] 啟動中..."
    & 'C:\Users\JS\Desktop\base\AgentGPT\platform\start_backend.ps1'
}

# --- 前端 (port 3001) ---
$fe = Get-NetTCPConnection -LocalPort 3001 -State Listen -ErrorAction SilentlyContinue
if ($fe) {
    Write-Host "[前端] Port 3001 已在運行 (PID $($fe.OwningProcess))，跳過"
} else {
    Write-Host "[前端] 啟動中..."
    & 'C:\Users\JS\Desktop\base\AgentGPT\next\start_frontend.ps1'
}

Write-Host "=== 完成 ==="
Write-Host "後端: http://localhost:3000 (TWSE 資料來源)"
Write-Host "前端: http://localhost:3001 (操作介面)"
