# 獨立啟動前端 production server（WMI 獨立進程，關閉本視窗不會影響）
# 前置條件：已執行過 next build（存在 .next/BUILD_ID）

# 檢查 production build 是否存在
if (-not (Test-Path -LiteralPath "C:\Users\JS\Desktop\base\AgentGPT\next\.next\BUILD_ID")) {
    Write-Host "找不到 production build！請先建置："
    Write-Host "  cd C:\Users\JS\Desktop\base\AgentGPT\next"
    Write-Host "  npm run build"
    exit 1
}

# 檢查 port 3001 是否已被佔用
$existing = Get-NetTCPConnection -LocalPort 3001 -State Listen -ErrorAction SilentlyContinue
if ($existing) {
    Write-Host "Port 3001 已被佔用 (PID $($existing.OwningProcess))，前端可能已在運行。"
    Write-Host "網址: http://localhost:3001"
    exit 0
}

# 注意：命令必須用單引號字串，雙引號 + 反引號轉義會導致 cmd.exe 啟動失敗
$cmdLine = 'cmd.exe /c "cd /d C:\Users\JS\Desktop\base\AgentGPT\next && C:\Progra~1\nodejs\node.exe node_modules/next/dist/bin/next start -p 3001 >> C:\Users\JS\AppData\Local\Temp\opencode\frontend.log 2>&1"'

$result = Invoke-CimMethod -ClassName Win32_Process -MethodName Create -Arguments @{
    CommandLine = $cmdLine
}

if ($result.ReturnValue -eq 0) {
    Write-Host "前端啟動中，ProcessId: $($result.ProcessId)"
    Write-Host "網址: http://localhost:3001"
} else {
    Write-Host "啟動失敗，ReturnValue: $($result.ReturnValue)"
}
