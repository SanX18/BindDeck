import re

with open('src/main.cpp', 'r', encoding='utf-8') as f:
    c = f.read()

# Replace all potentiometer variables and functions with Encoder logic
c = re.sub(
    r'// Potentiometer.*?void saveConfig\(\) \{',
    r'''// Encoder
#define ENCODER_CLK 18
#define ENCODER_DT 19
#define ENCODER_SW 5

const int8_t enc_states[] = {0, -1, 1, 0, 1, 0, 0, -1, -1, 0, 0, 1, 0, 1, -1, 0};
volatile int encoderSteps = 0;
volatile uint8_t old_AB = 0;

void IRAM_ATTR readEncoder() {
  old_AB <<= 2;
  uint8_t current = 0;
  if (digitalRead(ENCODER_CLK)) current |= 0x02;
  if (digitalRead(ENCODER_DT)) current |= 0x01;
  old_AB |= (current & 0x03);
  encoderSteps += enc_states[(old_AB & 0x0f)];
}

// Pins
const int SWITCH_PINS[8] = {13, 12, 14, 27, 26, 25, 33, 32};
const uint8_t MACRO_KEYS[8] = {KEY_F13, KEY_F14, KEY_F15, KEY_F16, KEY_F17, KEY_F18, KEY_F19, KEY_F20};
Bounce2::Button switches[8];
Bounce2::Button menuBtn;

void saveConfig() {''', c, flags=re.DOTALL)

# Remove loadConfig potentiometer lines
c = re.sub(r'  potRawMin = preferences\.getInt\("potRawMin", 400\);\n.*?  potTrackMax = 0;\n', '', c, flags=re.DOTALL)
# Remove updatePotCalibration function
c = re.sub(r'void updatePotCalibration\(int raw\) \{.*?\}\n', '', c, flags=re.DOTALL)

# Setup: replace Potentiometer setup with Encoder
c = re.sub(r'// Potentiometer setup\n.*?// potLastPercent stays -1 so the loop initializes it on first read\n',
r'''// Encoder setup
  pinMode(ENCODER_CLK, INPUT_PULLUP);
  pinMode(ENCODER_DT, INPUT_PULLUP);
  pinMode(ENCODER_SW, INPUT_PULLUP);
  attachInterrupt(digitalPinToInterrupt(ENCODER_CLK), readEncoder, CHANGE);
  attachInterrupt(digitalPinToInterrupt(ENCODER_DT), readEncoder, CHANGE);
''', c, flags=re.DOTALL)

# Loop: replace Potentiometer logic with Encoder logic
c = re.sub(r'    // --- Dynamic Range Tracking ---.*?actionStartTime = millis\(\);\n      \}\n    \}',
r'''    // --- Encoder Button (Programmable) ---
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
    }''', c, flags=re.DOTALL)

# handleEncoderAction: Add encMode 5 (App Vol)
c = re.sub(r'\} else if \(encMode == 3\) \{ // Undo / Redo\n    bleKeyboard\.press\(KEY_LEFT_CTRL\);\n    bleKeyboard\.write\(forward \? \'y\' : \'z\'\);\n    bleKeyboard\.releaseAll\(\);\n  \}',
r'''} else if (encMode == 3) { // Undo / Redo
    bleKeyboard.press(KEY_LEFT_CTRL);
    bleKeyboard.write(forward ? 'y' : 'z');
    bleKeyboard.releaseAll();
  } else if (encMode == 5) { // App Volume
    bleKeyboard.write(forward ? KEY_F22 : KEY_F21);
  }''', c, flags=re.DOTALL)

# Allow encMode up to 5
c = c.replace('if (encMode < 0 || encMode > 3) encMode = 0;', 'if (encMode < 0 || encMode > 5) encMode = 0;')

# Also restore the saveConfig for potRawMin which is gone
c = re.sub(r'  preferences\.putInt\("potRawMin", potRawMin\);\n  preferences\.putInt\("potRawMax", potRawMax\);\n', '', c, flags=re.DOTALL)

# Remove readPotPercent
c = re.sub(r'int readPotPercent\(int raw\) \{.*?\}\n', '', c, flags=re.DOTALL)
# Remove readPotRaw
c = re.sub(r'// Returns averaged raw ADC reading from potentiometer.*?int readPotRaw\(\) \{.*?\}\n', '', c, flags=re.DOTALL)


with open('src/main.cpp', 'w', encoding='utf-8') as f:
    f.write(c)

print("Done")
