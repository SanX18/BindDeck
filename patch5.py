import re
with open('src/main.cpp', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix drawAction for encMode
old_draw = """    } else if (encMode == 3) {
      display.setCursor(38, 28);
      display.print("UNDO/REDO");
    }"""
new_draw = """    } else if (encMode == 3) {
      display.setCursor(38, 28);
      display.print("UNDO/REDO");
    } else {
      display.setCursor(38, 28);
      display.print("APP VOL");
    }"""
content = content.replace(old_draw, new_draw)

# Limit diff in loop and add debug
old_loop = """      int diff = currentSteps - lastEncoderSteps;
      
      for(int i = 0; i < abs(diff); i++) {"""
new_loop = """      int diff = currentSteps - lastEncoderSteps;
      if (diff > 3) diff = 3;
      if (diff < -3) diff = -3;
      Serial.print("Encoder turned! Diff: ");
      Serial.println(diff);
      
      for(int i = 0; i < abs(diff); i++) {"""
content = content.replace(old_loop, new_loop)

with open('src/main.cpp', 'w', encoding='utf-8') as f:
    f.write(content)
print("Patch 5 applied.")
