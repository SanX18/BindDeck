with open('src/main.cpp', 'r', encoding='utf-8') as f:
    c = f.read()
c = c.replace("actionStartTime = millis();", 'actionStartTime = millis();\n          Serial.print("SW_PRESSED:");\n          Serial.println(i);')
with open('src/main.cpp', 'w', encoding='utf-8') as f:
    f.write(c)
print("Patched.")
