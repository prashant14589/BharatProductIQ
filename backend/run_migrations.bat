@echo off
REM Run migrations - no PowerShell activation needed
cd /d "%~dp0"
.\venv\Scripts\python.exe -m alembic upgrade head
pause
