@echo off
cd /d "%~dp0"
python pc_monitor.py
if %errorlevel% neq 0 (
    echo.
    echo The script has failed. Maybe 'python' is not recognized.
    echo Trying with 'py pc_monitor.py'...
    py pc_monitor.py
)
pause
