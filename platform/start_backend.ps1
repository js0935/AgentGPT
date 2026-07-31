# 獨立啟動後端（使用 WMI，進程不屬於當前 shell，不受 shell 終止影響）
$cmdLine = "cmd.exe /c set PYTHONPATH=C:\Users\JS\Desktop\base\AgentGPT\platform && C:\Users\JS\AppData\Local\pypoetry\Cache\virtualenvs\reworkd-platform-vQfEAOYy-py3.14\Scripts\python.exe -m reworkd_platform --host 0.0.0.0 --port 3000"
$workdir = "C:\Users\JS\Desktop\base\AgentGPT\platform"

$result = Invoke-CimMethod -ClassName Win32_Process -MethodName Create -Arguments @{
    CommandLine = $cmdLine
    CurrentDirectory = $workdir
}

if ($result.ReturnValue -eq 0) {
    Write-Host "Backend 啟動成功，ProcessId: $($result.ProcessId)"
} else {
    Write-Host "啟動失敗，ReturnValue: $($result.ReturnValue)"
}
