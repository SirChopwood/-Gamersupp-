@echo off
:Start
for /D %%i in (.\*) do (cd "%%i" && git pull && cd..)
"venv\Scripts\python.exe" "Scripts\Main.py"
:: Wait 30 seconds before restarting.
TIMEOUT /T 30
GOTO:Start