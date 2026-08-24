import re

with open('src/main.cpp', 'r', encoding='utf-8') as f:
    content = f.read()

# Increase arrays
content = content.replace("int keyAnims[8] = {-1, -1, -1, -1, -1, -1, -1, -1};", "int keyAnims[9] = {-1, -1, -1, -1, -1, -1, -1, -1, -1};")
content = content.replace('String keyTexts[8] = {"", "", "", "", "", "", "", ""};', 'String keyTexts[9] = {"", "", "", "", "", "", "", "", ""};')

# Fix loops in loadConfig and processCommand
content = content.replace('for(int i=0; i<8; i++) {', 'for(int i=0; i<9; i++) {')
content = content.replace('if (idx >= 0 && idx < 8) {', 'if (idx >= 0 && idx < 9) {')

# Wait, `lastActionKeyIndex` is checked in drawAction
content = content.replace('else if (lastActionKeyIndex >= 0 && lastActionKeyIndex < 8) {', 'else if (lastActionKeyIndex >= 0 && lastActionKeyIndex < 9) {')

# The button index in processCommand CFG:TXT: is 8 (since F21 is 21-13 = 8).
# Wait, data.substring(8, 9).toInt() will parse "8" correctly.
# But what if they have F13 to F22? "CFG:TXT:8:Hello" works.

# Encoder button press logic
old_enc_sw = """    // --- Encoder Button (Mute) ---
    if (digitalRead(ENCODER_SW) == LOW) {
      if (millis() - lastEncoderButtonPress > 200) {
        if (bleKeyboard.isConnected()) {
          bleKeyboard.write(KEY_MEDIA_MUTE);
        }
        lastActionKeyIndex = -1; // -1 animates the mic icon
        currentState = STATE_ACTION;
        actionStartTime = millis();
        lastEncoderButtonPress = millis();
      }
    }"""
    
new_enc_sw = """    // --- Encoder Button (Programmable) ---
    if (digitalRead(ENCODER_SW) == LOW) {
      if (millis() - lastEncoderButtonPress > 200) {
        if (bleKeyboard.isConnected()) {
          bleKeyboard.press(KEY_F21);
          delay(10);
          bleKeyboard.releaseAll();
        }
        lastActionKeyIndex = 8;
        currentState = STATE_ACTION;
        actionStartTime = millis();
        lastEncoderButtonPress = millis();
      }
    }"""

content = content.replace(old_enc_sw, new_enc_sw)

with open('src/main.cpp', 'w', encoding='utf-8') as f:
    f.write(content)

print("Firmware patched.")
