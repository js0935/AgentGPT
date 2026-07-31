# 一鍵啟動 AgentGPT（資料庫 3307 + 後端 3000 + 前端 3001）
# 用法: powershell -NoProfile -ExecutionPolicy Bypass -File start_all.ps1
#       或直接雙擊 start_all.bat

[Console]::OutputEncoding = New-Object System.Text.UTF8Encoding($false)

function Wait-Port {
    param([int]$Port, [int]$Retries = 15)
    for ($i = 1; $i -le $Retries; $i++) {
        if (Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue) {
            return $true
        }
        Start-Sleep -Seconds 1
    }
    return $false
}

Write-Host "=== AgentGPT 啟動器 ==="

# --- 資料庫 (MariaDB port 3307) ---
$db = Get-NetTCPConnection -LocalPort 3307 -State Listen -ErrorAction SilentlyContinue
if ($db) {
    Write-Host "[資料庫] Port 3307 已在運行 (PID $($db.OwningProcess))，跳過"
} else {
    Write-Host "[資料庫] MariaDB 啟動中..."
    & 'C:\Users\JS\Desktop\base\AgentGPT\start_mariadb.ps1'
    if (-not (Wait-Port 3307)) {
        Write-Host "[資料庫] 啟動逾時！請檢查 C:\Users\JS\AppData\Local\Temp\opencode\mariadb.log"
        exit 1
    }
    Write-Host "[資料庫] 就緒"
}

# --- 後端 (port 3000) ---
$be = Get-NetTCPConnection -LocalPort 3000 -State Listen -ErrorAction SilentlyContinue
if ($be) {
    Write-Host "[後端] Port 3000 已在運行 (PID $($be.OwningProcess))，跳過"
} else {
    Write-Host "[後端] 啟動中..."
    & 'C:\Users\JS\Desktop\base\AgentGPT\platform\start_backend.ps1'
    if (-not (Wait-Port 3000)) {
        Write-Host "[後端] 啟動逾時！請檢查 C:\Users\JS\AppData\Local\Temp\opencode\backend.log"
        exit 1
    }
    Write-Host "[後端] 就緒"
}

# --- 前端 (port 3001) ---
$fe = Get-NetTCPConnection -LocalPort 3001 -State Listen -ErrorAction SilentlyContinue
if ($fe) {
    Write-Host "[前端] Port 3001 已在運行 (PID $($fe.OwningProcess))，跳過"
} else {
    Write-Host "[前端] 啟動中..."
    & 'C:\Users\JS\Desktop\base\AgentGPT\next\start_frontend.ps1'
    if (-not (Wait-Port 3001)) {
        Write-Host "[前端] 啟動逾時！請檢查 C:\Users\JS\AppData\Local\Temp\opencode\frontend.log"
        exit 1
    }
    Write-Host "[前端] 就緒"
}

Write-Host "=== 全部就緒 ==="
Write-Host "後端: http://localhost:3000 (TWSE 資料來源)"
Write-Host "前端: http://localhost:3001 (操作介面)"
Write-Host "正在開啟瀏覽器..."
Start-Process "http://localhost:3001"
