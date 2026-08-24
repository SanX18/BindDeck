copy /Y "..\.pio\build\esp32dev\firmware.bin" "firmware.bin"
python -m PyInstaller --noconfirm --onedir --windowed --icon="static/logo.ico" --add-data "templates;templates/" --add-data "static;static/" --add-data "LibreHardwareMonitor;LibreHardwareMonitor/" --add-data "firmware.bin;." --collect-data esptool "pc_monitor.py" --name "BindDeck"
