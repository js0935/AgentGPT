# 獨立啟動 MariaDB（port 3307，WMI 獨立進程，關閉本視窗不會影響）

[Console]::OutputEncoding = New-Object System.Text.UTF8Encoding($false)

# 檢查 port 3307 是否已被佔用
$existing = Get-NetTCPConnection -LocalPort 3307 -State Listen -ErrorAction SilentlyContinue
if ($existing) {
    Write-Host "Port 3307 已被佔用 (PID $($existing.OwningProcess))，MariaDB 可能已在運行。"
    exit 0
}

# 注意：命令必須用單引號字串，雙引號 + 反引號轉義會導致 cmd.exe 啟動失敗
$cmdLine = 'cmd.exe /c "cd /d C:\Users\JS\Desktop\base\mariadb-11.4.5-winx64\bin && mysqld.exe --defaults-file=C:\Users\JS\Desktop\base\mariadb-11.4.5-winx64\data\my.ini --console >> C:\Users\JS\AppData\Local\Temp\opencode\mariadb.log 2>&1"'

$result = Invoke-CimMethod -ClassName Win32_Process -MethodName Create -Arguments @{
    CommandLine = $cmdLine
}

if ($result.ReturnValue -eq 0) {
    Write-Host "MariaDB 啟動中，ProcessId: $($result.ProcessId)"
} else {
    Write-Host "啟動失敗，ReturnValue: $($result.ReturnValue)"
}
