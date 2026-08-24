import re

with open('src/main.cpp', 'r', encoding='utf-8') as f:
    c = f.read()

# 1. Remove Potentiometer definitions and add Encoder definitions
c = re.sub(r'#define POT_PIN 34\n#define POT_SAMPLES 10\n', 
           '#define ENCODER_CLK 18\n#define ENCODER_DT 19\n#define ENCODER_SW 5\n', c)

# 2. Replace readPotRaw with readEncoder and variables
pot_func = r'// Returns averaged raw ADC reading from potentiometer.*?delayMicroseconds\(200\);\n    \}\n    return sum / POT_SAMPLES;\n  \}'
enc_func = """const int8_t enc_states[] = {0, -1, 1, 0, 1, 0, 0, -1, -1, 0, 0, 1, 0, 1, -1, 0};
volatile int encoderSteps = 0;
volatile uint8_t old_AB = 0;

void IRAM_ATTR readEncoder() {
  old_AB <<= 2;
  uint8_t current = 0;
  if (digitalRead(ENCODER_CLK)) current |= 0x02;
  if (digitalRead(ENCODER_DT)) current |= 0x01;
  old_AB |= (current & 0x03);
  encoderSteps += enc_states[(old_AB & 0x0f)];
}"""
c = re.sub(pot_func, enc_func, c, flags=re.DOTALL)

# 3. Setup: replace Potentiometer setup
pot_setup = r'// Potentiometer setup\n  analogReadResolution\(12\);.*?// potLastPercent stays -1 so the loop initializes it on first read'
enc_setup = """// Encoder setup
  pinMode(ENCODER_CLK, INPUT_PULLUP);
  pinMode(ENCODER_DT, INPUT_PULLUP);
  pinMode(ENCODER_SW, INPUT_PULLUP);
  attachInterrupt(digitalPinToInterrupt(ENCODER_CLK), readEncoder, CHANGE);
  attachInterrupt(digitalPinToInterrupt(ENCODER_DT), readEncoder, CHANGE);"""
c = re.sub(pot_setup, enc_setup, c, flags=re.DOTALL)

# 4. Loop: replace Potentiometer tracking with Encoder tracking
pot_loop = r'// --- Dynamic Range Tracking ---.*?actionStartTime = millis\(\);\n      \}\n    \}'
enc_loop = """// --- Encoder Button (Programmable) ---
    static unsigned long lastEncoderButtonPress = 0;
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
    }

    // --- Rotary Encoder ---
    static int lastEncoderSteps = 0;
    if (encoderSteps / 4 != lastEncoderSteps / 4) {
      noInterrupts();
      int currentSteps = encoderSteps;
      interrupts();
      
      int diff = (currentSteps / 4) - (lastEncoderSteps / 4);
      if (diff > 3) diff = 3;
      if (diff < -3) diff = -3;
      
      for(int i = 0; i < abs(diff); i++) {
        bool forward = (diff > 0);
        handleEncoderAction(forward);
        delay(15);
        
        if (encMode == 0) {
           visualVolume += forward ? 4 : -4;
           if (visualVolume < 0) visualVolume = 0;
           if (visualVolume > 100) visualVolume = 100;
        }
      }
      
      lastEncoderSteps = currentSteps;
      lastActionKeyIndex = -3;
      currentState = STATE_ACTION;
      actionStartTime = millis();
    }"""
c = re.sub(pot_loop, enc_loop, c, flags=re.DOTALL)

# 5. Fix handleEncoderAction for APP VOL
old_handle = r'\} else if \(encMode == 3\) \{ // Undo / Redo\n    bleKeyboard\.press\(KEY_LEFT_CTRL\);\n    bleKeyboard\.write\(forward \? \'y\' : \'z\'\);\n    bleKeyboard\.releaseAll\(\);\n  \}'
new_handle = """} else if (encMode == 3) { // Undo / Redo
    bleKeyboard.press(KEY_LEFT_CTRL);
    bleKeyboard.write(forward ? 'y' : 'z');
    bleKeyboard.releaseAll();
  } else if (encMode == 5) { // App Volume
    bleKeyboard.write(forward ? KEY_F22 : KEY_F21);
  }"""
c = re.sub(old_handle, new_handle, c)

# 6. Fix encMode clamping in loadConfig
c = c.replace('if (encMode < 0 || encMode > 3) encMode = 0;', 'if (encMode < 0 || encMode > 5) encMode = 0;')

with open('src/main.cpp', 'w', encoding='utf-8') as f:
    f.write(c)

print("Encoder fixes restored!")
