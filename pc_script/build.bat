@echo off
echo Construyendo BindDeck.exe...
python -m PyInstaller --noconfirm --onedir --windowed --icon="static/logo.ico" --add-data "templates;templates/" --add-data "static;static/"  "pc_monitor.py" --name "BindDeck"
echo Terminado. El ejecutable esta en la carpeta 'dist\BindDeck\BindDeck.exe'
pause
