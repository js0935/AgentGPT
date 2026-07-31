# 獨立啟動後端（使用 WMI，進程不屬於當前 shell，不受 shell 終止影響）
# 注意：命令必須用單引號字串，雙引號 + 反引號轉義會導致 cmd.exe 啟動失敗
$cmdLine = 'cmd.exe /c "cd /d C:\Users\JS\Desktop\base\AgentGPT\platform && set PYTHONPATH=C:\Users\JS\Desktop\base\AgentGPT\platform && C:\Users\JS\AppData\Local\pypoetry\Cache\virtualenvs\reworkd-platform-vQfEAOYy-py3.14\Scripts\python.exe -m reworkd_platform --host 0.0.0.0 --port 3000 >> C:\Users\JS\AppData\Local\Temp\opencode\backend.log 2>&1"'

$result = Invoke-CimMethod -ClassName Win32_Process -MethodName Create -Arguments @{
    CommandLine = $cmdLine
}

if ($result.ReturnValue -eq 0) {
    Write-Host "Backend 啟動中，ProcessId: $($result.ProcessId)"
} else {
    Write-Host "啟動失敗，ReturnValue: $($result.ReturnValue)"
}
