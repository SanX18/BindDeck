@echo off
echo Construyendo MacroDeck.exe...
python -m PyInstaller --noconfirm --onedir --windowed --icon="static/logo.ico" --add-data "templates;templates/" --add-data "static;static/"  "pc_monitor.py" --name "MacroDeck"
echo Terminado. El ejecutable esta en la carpeta 'dist\MacroDeck\MacroDeck.exe'
pause
