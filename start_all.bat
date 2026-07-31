@echo off
rem 雙擊即可啟動 AgentGPT（後端 3000 + 前端 3001）
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0start_all.ps1"
echo.
pause
