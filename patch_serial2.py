with open('src/main.cpp', 'r', encoding='utf-8') as f:
    c = f.read()

old_block = """      for(int i = 0; i < 8; i++) {
        if(switches[i].pressed()) {
          if(bleKeyboard.isConnected()) {
            bleKeyboard.press(MACRO_KEYS[i]);
            delay(10);
            bleKeyboard.releaseAll();
          }
          lastActionKeyIndex = i;
          currentState = STATE_ACTION;
          actionStartTime = millis();
        }
      }"""

new_block = """      for(int i = 0; i < 8; i++) {
        if(switches[i].pressed()) {
          Serial.print("SW_PRESSED:");
          Serial.println(i);
          if(bleKeyboard.isConnected()) {
            bleKeyboard.press(MACRO_KEYS[i]);
            delay(10);
            bleKeyboard.releaseAll();
          }
          lastActionKeyIndex = i;
          currentState = STATE_ACTION;
          actionStartTime = millis();
        }
      }"""

c = c.replace(old_block, new_block)
with open('src/main.cpp', 'w', encoding='utf-8') as f:
    f.write(c)
print("Patched correctly.")
