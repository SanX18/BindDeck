import re
with open('src/main.cpp', 'r', encoding='utf-8') as f:
    content = f.read()

# Force encMode to 0 if it's invalid or 5
content = content.replace("encMode = preferences.getInt(\"encMode\", 0);", "encMode = preferences.getInt(\"encMode\", 0);\n  if (encMode < 0 || encMode > 3) encMode = 0;")

# Add a small delay between BLE sends to ensure Windows registers them
old_loop = """      for(int i = 0; i < abs(diff); i++) {
        bool forward = (diff > 0);
        handleEncoderAction(forward);
        
        if (encMode == 0) {"""
new_loop = """      for(int i = 0; i < abs(diff); i++) {
        bool forward = (diff > 0);
        handleEncoderAction(forward);
        delay(15); // ESPERA para que el Bluetooth procese la tecla
        
        if (encMode == 0) {"""
content = content.replace(old_loop, new_loop)

# Fix drawAction just in case
content = content.replace('display.print("APP VOL");', 'display.print("MODE "); display.print(encMode);')

with open('src/main.cpp', 'w', encoding='utf-8') as f:
    f.write(content)
print("Patch 6 applied.")
