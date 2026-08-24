import sys

with open('src/main.cpp', 'r', encoding='utf-8') as f:
    c = f.read()

# 1. Start of file
a1 = """// Potentiometer
const int POT_PIN      = 34;
const int POT_SAMPLES  = 32;  // Increased for better noise immunity
const int POT_DEADZONE = 4;   // Reduced deadzone for better sensitivity

// Calibrated range — saved to flash, updated automatically
int potRawMin = 400;   // Defaults: conservative. Updated when pot hits stops.
int potRawMax = 3700;

// Tracking vars (NOT saved — reset every boot, initialized to ADC extremes)
// Starting at 4095/0 means ANY real reading immediately starts tracking.
int   potTrackMin     = 32767;
int   potTrackMax     = 0;
unsigned long potTrackMinSince = 0;
unsigned long potTrackMaxSince = 0;

int potLastPercent = -1;
int potSentVolume  = -1;
unsigned long lastPotChange = 0;"""
b1 = """#define ENCODER_CLK 18
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
}"""
c = c.replace(a1, b1)

# 2. saveConfig
a2 = """  preferences.putInt("potRawMin", potRawMin);
  preferences.putInt("potRawMax", potRawMax);"""
b2 = ""
c = c.replace(a2, b2)

# 3. loadConfig
a3 = """  potRawMin = preferences.getInt("potRawMin", 400);
  potRawMax = preferences.getInt("potRawMax", 3700);
  
  potTrackMin = 32767;
  potTrackMax = 0;"""
b3 = ""
c = c.replace(a3, b3)
c = c.replace('if (encMode < 0 || encMode > 3) encMode = 0;', 'if (encMode < 0 || encMode > 5) encMode = 0;')

# 4. POT functions
a4 = """// Returns averaged raw ADC reading from potentiometer
int readPotRaw() {
  long sum = 0;
  for (int i = 0; i < POT_SAMPLES; i++) {
    sum += analogRead(POT_PIN);
    delayMicroseconds(200);
  }
  return (int)(sum / POT_SAMPLES);
}

// Converts raw reading to 0-100% using dynamic calibration bounds
int readPotPercent(int raw) {
  int pct = (potRawMax > potRawMin) ? map(raw, potRawMin, potRawMax, 0, 100) : 0;
  if (pct < 0) pct = 0;
  if (pct > 100) pct = 100;
  return pct;
}

// Continuously refines the minimum and maximum physical bounds
void updatePotCalibration(int raw) {
  const int MARGIN = 20;       // Stop threshold margin
  const int STABLE_MS = 500;   // Needs to stay at the extreme for 500ms to calibrate
  
  // Update Minimum
  if (raw < potTrackMin - MARGIN) {
    potTrackMin = raw;
    potTrackMinSince = millis();
  } else if (raw <= potTrackMin + MARGIN && millis() - potTrackMinSince >= STABLE_MS) {
    if (potTrackMin < potRawMin) {
      potRawMin = potTrackMin;
      saveConfig();
    }
  }
  
  // Update Maximum
  if (raw > potTrackMax + MARGIN) {
    potTrackMax = raw;
    potTrackMaxSince = millis();
  } else if (raw >= potTrackMax - MARGIN && millis() - potTrackMaxSince >= STABLE_MS) {
    if (potTrackMax > potRawMax) {
      potRawMax = potTrackMax;
      saveConfig();
    }
  }
}"""
b4 = ""
c = c.replace(a4, b4)

# 5. setup
a5 = """  // Potentiometer setup
  analogReadResolution(12);          // 12-bit: 0-4095
  analogSetAttenuation(ADC_11db);    // Full 0-3.3V range
  // potLastPercent stays -1 so the loop initializes it on first read"""
b5 = """  // Encoder setup
  pinMode(ENCODER_CLK, INPUT_PULLUP);
  pinMode(ENCODER_DT, INPUT_PULLUP);
  pinMode(ENCODER_SW, INPUT_PULLUP);
  attachInterrupt(digitalPinToInterrupt(ENCODER_CLK), readEncoder, CHANGE);
  attachInterrupt(digitalPinToInterrupt(ENCODER_DT), readEncoder, CHANGE);"""
c = c.replace(a5, b5)

# 6. loop
a6 = """    // --- Dynamic Range Tracking ---
    // Instantly adapts to your potentiometer's real physical range without deadzones.
    int raw = readPotRaw();
    static int pMin = 4095;
    static int pMax = 0;
    if (raw < pMin) pMin = raw;
    if (raw > pMax) pMax = raw;
    
    int range = pMax - pMin;
    if (range < 500) range = 4095; // Default safe range before we discover the real one
    
    // We want EXACTLY 55 steps (110% volume) over the entire physical rotation.
    // This perfectly covers 0-100% in Windows and avoids stopping at 50%.
    int rawPerStep = range / 55; 

    // Initialize on first read
    static int potLastRaw = -1;
    if (potLastRaw == -1) {
      potLastRaw = raw;
    }

    // Non-blocking smooth accumulator
    static unsigned long lastPotSend = 0;
    int diff = raw - potLastRaw;
    
    if (abs(diff) >= rawPerStep) {
      if (millis() - lastPotSend > 15) {
        bool forward = diff > 0;
        
        handleEncoderAction(forward);
        
        // Advance our tracker by exactly one step (leaving remainder in the accumulator for slow turns)
        potLastRaw += forward ? rawPerStep : -rawPerStep;
        lastPotSend = millis();
        
        if (encMode == 0) {
           visualVolume += forward ? 2 : -2;
           if (visualVolume < 0) visualVolume = 0;
           if (visualVolume > 100) visualVolume = 100;
        }
        lastActionKeyIndex = -3;
        currentState = STATE_ACTION;
        actionStartTime = millis();
      }
    }"""
b6 = """    // --- Encoder Button (Programmable) ---
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
c = c.replace(a6, b6)

a7 = """} else if (encMode == 3) { // Undo / Redo
    bleKeyboard.press(KEY_LEFT_CTRL);
    bleKeyboard.write(forward ? 'y' : 'z');
    bleKeyboard.releaseAll();
  }"""
b7 = """} else if (encMode == 3) { // Undo / Redo
    bleKeyboard.press(KEY_LEFT_CTRL);
    bleKeyboard.write(forward ? 'y' : 'z');
    bleKeyboard.releaseAll();
  } else if (encMode == 5) { // App Volume
    bleKeyboard.write(forward ? KEY_F22 : KEY_F21);
  }"""
c = c.replace(a7, b7)

with open('src/main.cpp', 'w', encoding='utf-8') as f:
    f.write(c)

print("Restored!")
