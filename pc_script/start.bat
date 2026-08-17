@echo off
cd /d "%~dp0"
python pc_monitor.py
if %errorlevel% neq 0 (
    echo.
    echo El script ha fallado. Quiza 'python' no se reconoce.
    echo Intentando con 'py pc_monitor.py'...
    py pc_monitor.py
)
pause
