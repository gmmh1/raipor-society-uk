@echo off
setlocal
pwsh -File "%~dp0local-qwen-session.ps1" %*
endlocal