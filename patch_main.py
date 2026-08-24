import re

with open('src/main.cpp', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Replace variables
var_target = """// Potentiometer
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

var_replacement = """// Rotary Encoder KY-040
#define ENCODER_CLK 16
#define ENCODER_DT  17
#define ENCODER_SW  5

volatile int encoderSteps = 0;
int lastEncoderSteps = 0;
unsigned long lastEncoderButtonPress = 0;

// Switch Slider
#define SWITCH_SLIDER 18
bool lastSliderState = false;

// Interrupt para el encoder
void IRAM_ATTR readEncoder() {
  int dtValue = digitalRead(ENCODER_DT);
  if (dtValue == HIGH) {
    encoderSteps++;
  } else {
    encoderSteps--;
  }
}"""

content = content.replace(var_target, var_replacement)

# 2. Remove POT functions
pot_funcs = re.compile(r'// Returns averaged raw ADC reading from potentiometer.*?Serial\.print\(" max="\); Serial\.println\(potRawMax\);\n}', re.DOTALL)
content = re.sub(pot_funcs, '', content)

# 3. Setup replacement
setup_target = """  // Potentiometer setup
  analogReadResolution(12);          // 12-bit: 0-4095
  analogSetAttenuation(ADC_11db);    // Full 0-3.3V range
  // potLastPercent stays -1 so the loop initializes it on first read"""

setup_replacement = """  // Encoder y Switch setup
  pinMode(ENCODER_CLK, INPUT_PULLUP);
  pinMode(ENCODER_DT, INPUT_PULLUP);
  pinMode(ENCODER_SW, INPUT_PULLUP);
  pinMode(SWITCH_SLIDER, INPUT_PULLUP);
  attachInterrupt(digitalPinToInterrupt(ENCODER_CLK), readEncoder, FALLING);"""

content = content.replace(setup_target, setup_replacement)

# 4. Loop replacement
loop_target = """    // --- Dynamic Range Tracking ---
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

loop_replacement = """    // --- Rotary Encoder ---
    if (encoderSteps != lastEncoderSteps) {
      bool forward = (encoderSteps > lastEncoderSteps);
      
      handleEncoderAction(forward);
      
      if (encMode == 0) {
         visualVolume += forward ? 2 : -2;
         if (visualVolume < 0) visualVolume = 0;
         if (visualVolume > 100) visualVolume = 100;
      }
      
      lastEncoderSteps = encoderSteps;
      lastActionKeyIndex = -3;
      currentState = STATE_ACTION;
      actionStartTime = millis();
    }
    
    // --- Encoder Button (Mute) ---
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
    }
    
    // --- Switch Slider (Play/Pause) ---
    bool isSliderOn = (digitalRead(SWITCH_SLIDER) == LOW);
    if (isSliderOn != lastSliderState) {
      if (bleKeyboard.isConnected()) {
        bleKeyboard.write(KEY_MEDIA_PLAY_PAUSE);
      }
      lastSliderState = isSliderOn;
      delay(50);
    }"""

content = content.replace(loop_target, loop_replacement)

# Remove potRawMin/potRawMax from saveConfig/loadConfig
content = re.sub(r'  preferences\.putInt\("potRawMin", potRawMin\);\n', '', content)
content = re.sub(r'  preferences\.putInt\("potRawMax", potRawMax\);\n', '', content)
content = re.sub(r'  potRawMin = preferences\.getInt\("potRawMin", 400\);\n', '', content)
content = re.sub(r'  potRawMax = preferences\.getInt\("potRawMax", 3700\);\n', '', content)

with open('src/main.cpp', 'w', encoding='utf-8') as f:
    f.write(content)

print("Patch applied.")
