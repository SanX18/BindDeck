Set WshShell = CreateObject("WScript.Shell")
WshShell.CurrentDirectory = "C:\Users\panca\Documents\Projectos ESP32\pc_script"
WshShell.Run "cmd.exe /c python pc_monitor.py > log.txt 2>&1", 0, False
