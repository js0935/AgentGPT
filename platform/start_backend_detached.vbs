' 以完全獨立的程序啟動後端（不受父 shell 影響）
Dim shell
Set shell = CreateObject("WScript.Shell")

' 設定環境變數
Dim envStr
envStr = "PYTHONPATH=C:\Users\JS\Desktop\base\AgentGPT\platform"

' 啟動後端（獨立程序，不等待）
shell.Run "cmd.exe /c set " & envStr & " && C:\Users\JS\AppData\Local\pypoetry\Cache\virtualenvs\reworkd-platform-vQfEAOYy-py3.14\Scripts\python.exe -m reworkd_platform --host 0.0.0.0 --port 3000", 0, False

Set shell = Nothing
