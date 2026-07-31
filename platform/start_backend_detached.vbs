' 以完全獨立的程序啟動後端（使用 WMI，不受父 shell 影響）
Dim locator, service, inParams, outParams
Set locator = CreateObject("WbemScripting.SWbemLocator")
Set service = locator.ConnectServer(".", "root\cimv2")

Set inParams = service.Get("Win32_Process").Methods_("Create").InParameters.SpawnInstance_()
inParams.CommandLine = "cmd.exe /c set PYTHONPATH=C:\Users\JS\Desktop\base\AgentGPT\platform && C:\Users\JS\AppData\Local\pypoetry\Cache\virtualenvs\reworkd-platform-vQfEAOYy-py3.14\Scripts\python.exe -m reworkd_platform --host 0.0.0.0 --port 3000"
inParams.CurrentDirectory = "C:\Users\JS\Desktop\base\AgentGPT\platform"

Set outParams = service.ExecMethod_("Win32_Process", "Create", inParams)

Set locator = Nothing
