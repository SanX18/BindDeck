#include <Arduino.h>
#include <BleKeyboard.h>
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include <Bounce2.h>
#include <Preferences.h>
#include "RoboEyes.h"

#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64
#define OLED_RESET    -1
#define SCREEN_ADDRESS 0x3C

Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);
RoboEyes<Adafruit_SSD1306> eyes(display);
BleKeyboard bleKeyboard("MacroDeck", "Custom", 100);
Preferences preferences;

// Potentiometer
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
unsigned long lastPotChange = 0;

// Pins
const int SWITCH_PINS[8] = {13, 12, 14, 27, 26, 25, 33, 32};
const uint8_t MACRO_KEYS[8] = {KEY_F13, KEY_F14, KEY_F15, KEY_F16, KEY_F17, KEY_F18, KEY_F19, KEY_F20};
Bounce2::Button switches[8];

enum State {
  STATE_IDLE,
  STATE_ACTION,
  STATE_MENU,
  STATE_EYES
};
State currentState = STATE_IDLE;

// Telemetry Data
int cpu_temp = 0, cpu_usage = 0, gpu_temp = 0, gpu_usage = 0;

// Action Data
unsigned long actionStartTime = 0;
unsigned long lastEyeTime = 0;
unsigned long eyeStateStartTime = 0;
const unsigned long ACTION_DURATION = 800;
int lastActionKeyIndex = -1; // -1: mute, -2: preview, -3: volume
int visualVolume = 50;

// Config Data
int brightness = 255;
int animMode = 0; // 0: Circles, 1: Flash, 2: Minimal
int encMode = 0;  // 0: Volume, 1: Vertical Arrows, 2: Horizontal Arrows
int keyAnims[8] = {-1, -1, -1, -1, -1, -1, -1, -1}; // -1 means use global animMode
String keyTexts[8] = {"", "", "", "", "", "", "", ""};
int previewAnimOverride = -1;

void saveConfig() {
  preferences.begin("macrodeck", false);
  preferences.putInt("animMode", animMode);
  preferences.putInt("encMode", encMode);
  preferences.putInt("brightness", brightness);
  preferences.putBytes("keyAnims", keyAnims, sizeof(keyAnims));
  preferences.putInt("potRawMin", potRawMin);
  preferences.putInt("potRawMax", potRawMax);
  preferences.end();
}

// Forward declarations
void drawIdle();
void drawAction();
void drawMenu();
void drawUpdateScreen();
void drawMicIcon(int x, int y, uint16_t color, uint16_t bg);
void handleEncoderAction(bool forward);

void loadConfig() {
  preferences.begin("macrodeck", true);
  animMode = preferences.getInt("animMode", 0);
  encMode = preferences.getInt("encMode", 0);
  brightness = preferences.getInt("brightness", 255);
  for(int i=0; i<8; i++) {
    char key[10];
    sprintf(key, "kbanim%d", i);
    keyAnims[i] = preferences.getInt(key, -1);
    
    char keyTxt[10];
    sprintf(keyTxt, "kbtxt%d", i);
    keyTexts[i] = preferences.getString(keyTxt, "");
  }
  potRawMin = 32767; // Force reset auto-calibration
  potRawMax = 0;
  // cleared
  // potTrackMin/Max intentionally NOT loaded — reset to extremes every boot
  // so calibration can learn from the very first use each session
  potTrackMin = 32767;
  potTrackMax = 0;
  preferences.end();
}

// Returns averaged raw ADC reading from potentiometer
int readPotRaw() {
  long sum = 0;
  for (int i = 0; i < POT_SAMPLES; i++) {
    sum += analogRead(POT_PIN);
    delayMicroseconds(200);
  }
  return (int)(sum / POT_SAMPLES);
}

// Returns potentiometer position as 0-100% using calibrated range
int readPotPercent(int raw) {
  int pct = (potRawMax > potRawMin) ? map(raw, potRawMin, potRawMax, 0, 100) : 0;
  return constrain(pct, 0, 100);
}

// Auto-calibration: tracks the lowest and highest stable raw values seen.
// potTrackMin starts at 4095 so the first real reading always updates it.
// potTrackMax starts at 0 so the first real reading always updates it.
// Only commits to flash if the new extreme has been held for 700ms (no noise).
void updatePotCalibration(int raw) {
  const unsigned long STABLE_MS = 200;  // Reduced to calibrate faster
  const int           MARGIN    = 25;   // Increased tolerance to capture ends easily

  // ── Track minimum ──
  if (raw < potTrackMin - MARGIN) {
    // New lowest value seen: reset the timer
    potTrackMin     = raw;
    potTrackMinSince = millis();
  } else if (raw <= potTrackMin + MARGIN && millis() - potTrackMinSince >= STABLE_MS) {
    // Stable near the new low for 700ms → accept as calibrated minimum
    if (potTrackMin < potRawMin) {
      potRawMin = potTrackMin;
      saveConfig();
    }
  }

  // ── Track maximum ──
  if (raw > potTrackMax + MARGIN) {
    // New highest value seen: reset the timer
    potTrackMax     = raw;
    potTrackMaxSince = millis();
  } else if (raw >= potTrackMax - MARGIN && millis() - potTrackMaxSince >= STABLE_MS) {
    // Stable near the new high for 700ms → accept as calibrated maximum
    if (potTrackMax > potRawMax) {
      potRawMax = potTrackMax;
      saveConfig();
    }
  }

  // Serial debug — open Monitor at 115200 to watch calibration learn
  Serial.print("raw="); Serial.print(raw);
  Serial.print(" | calib min="); Serial.print(potRawMin);
  Serial.print(" max="); Serial.println(potRawMax);
}


void parseSerialData() {
  if (Serial.available() > 0) {
    String data = Serial.readStringUntil('\n');
    data.trim();
    
    // Config commands from PC App (e.g. CFG:ANIM:1)
    if (data.startsWith("CFG:ANIM:")) {
      animMode = data.substring(9).toInt();
      saveConfig();
    } else if (data.startsWith("CFG:ENC:")) {
      encMode = data.substring(8).toInt();
      saveConfig();
    } else if (data.startsWith("CFG:BRT:")) {
      brightness = data.substring(8).toInt();
      display.ssd1306_command(SSD1306_SETCONTRAST);
      display.ssd1306_command(brightness);
      saveConfig();
    } else if (data.startsWith("CFG:KB_ANIM:")) {
      String payload = data.substring(12);
      for(int i=0; i<8; i++) {
        int comma = payload.indexOf(',');
        if (comma != -1) {
          keyAnims[i] = payload.substring(0, comma).toInt();
          payload = payload.substring(comma+1);
        } else {
          keyAnims[i] = payload.toInt();
        }
      }
      saveConfig();
    } else if (data.startsWith("CFG:TXT:")) {
      int idx = data.substring(8, 9).toInt();
      String txt = data.substring(10);
      if (idx >= 0 && idx < 8) {
        keyTexts[idx] = txt;
        char pk[10];
        sprintf(pk, "kbtxt%d", idx);
        preferences.begin("macrodeck", false);
        preferences.putString(pk, txt);
        preferences.end();
      }
    } else if (data.startsWith("CMD:PREVIEW:")) {
      previewAnimOverride = data.substring(12).toInt();
      lastActionKeyIndex = -2;
      currentState = STATE_ACTION;
      actionStartTime = millis();
    } else if (data.startsWith("CMD:UPDATE")) {
      drawUpdateScreen();
    } else if (data.startsWith("CMD:SIMULATE:")) {
      lastActionKeyIndex = data.substring(13).toInt();
      currentState = STATE_ACTION;
      actionStartTime = millis();
    } else if (data.indexOf("C:") != -1 && data.indexOf("G:") != -1) {
      sscanf(data.c_str(), "C:%d,U:%d,G:%d,V:%d", &cpu_temp, &cpu_usage, &gpu_temp, &gpu_usage);
    }
  }
}

void drawIdle() {
  display.clearDisplay();

  if (cpu_temp > 85 || gpu_temp > 85) {
    if ((millis() / 500) % 2 == 0) { // Parpadeo cada 500ms
      display.fillRect(0, 0, 128, 64, SSD1306_WHITE);
      display.setTextColor(SSD1306_BLACK);
      display.setTextSize(2);
      display.setCursor(20, 15);
      display.println("ALERTA!");
      display.setTextSize(1);
      display.setCursor(15, 40);
      if (cpu_temp > 85) display.print("CPU TEMP ALTA: "); else display.print("GPU TEMP ALTA: ");
      display.println(cpu_temp > 85 ? cpu_temp : gpu_temp);
    }
  } else {
    display.setTextSize(1);
    display.setTextColor(SSD1306_WHITE);
    
    display.setCursor(0, 0);
    display.println("--- SYSTEM STATS ---");
    
    display.setCursor(0, 15);
    display.print("CPU Temp: "); display.print(cpu_temp); display.println(" C");
    display.setCursor(0, 25);
    display.print("CPU Load: "); display.print(cpu_usage); display.println(" %");

    display.setCursor(0, 40);
    display.print("GPU Temp: "); display.print(gpu_temp); display.println(" C");
    display.setCursor(0, 50);
    display.print("GPU Load: "); display.print(gpu_usage); display.println(" %");
  }

  display.display();
}

void drawUpdateScreen() {
  display.clearDisplay();
  
  // Dibujar ojos estáticos de concentración
  display.fillRoundRect(20, 10, 30, 25, 5, SSD1306_WHITE);
  display.fillRoundRect(78, 10, 30, 25, 5, SSD1306_WHITE);
  // Pupilas
  display.fillCircle(35, 22, 6, SSD1306_BLACK);
  display.fillCircle(93, 22, 6, SSD1306_BLACK);
  
  display.setTextSize(1);
  display.setTextColor(SSD1306_WHITE);
  display.setCursor(5, 45);
  display.println("ACTUALIZANDO...");
  display.setCursor(5, 55);
  display.println("NO DESCONECTAR!");
  
  display.display();
  
  // Bucle infinito, esperando el reinicio de esptool
  while(true) {
    delay(100);
  }
}

void drawMicIcon(int x, int y, uint16_t color, uint16_t bg) {
  int bw = 8;
  int bh = 14;
  
  // Clear a box behind the mic
  display.fillRoundRect(x - bw/2 - 6, y - bh/2 - 4, bw + 12, bh + 14, 2, bg);

  // Cup (drawn first)
  display.drawRoundRect(x - bw/2 - 4, y - bh/2 + 2, bw + 8, bh, 4, color);
  // Erase top half of cup
  display.fillRect(x - bw/2 - 5, y - bh/2 - 2, bw + 10, bh/2 + 4, bg); 

  // Mic body (drawn over the cup erase area)
  display.fillRoundRect(x - bw/2, y - bh/2, bw, bh, 3, color);
  
  // Stand
  display.drawLine(x, y + bh/2 + 2, x, y + bh/2 + 6, color);
  display.drawLine(x - 5, y + bh/2 + 6, x + 5, y + bh/2 + 6, color);
  
  // Diagonal slash
  display.drawLine(x - 12, y - 10, x + 12, y + 14, color);
  display.drawLine(x - 12, y - 9, x + 11, y + 14, color);
}

void drawAction() {
  display.clearDisplay();
  unsigned long elapsed = millis() - actionStartTime;
  
  if (lastActionKeyIndex == -3) {
    display.setTextSize(1);
    display.setTextColor(SSD1306_WHITE);
    if (encMode == 0) {
      display.setCursor(46, 15);
      display.print("VOLUME");
      display.drawRect(14, 35, 100, 10, SSD1306_WHITE);
      display.fillRect(14, 35, visualVolume, 10, SSD1306_WHITE);
    } else if (encMode == 1) {
      display.setCursor(52, 28);
      display.print("ZOOM");
    } else if (encMode == 2) {
      display.setCursor(52, 28);
      display.print("TABS");
    } else if (encMode == 3) {
      display.setCursor(38, 28);
      display.print("UNDO/REDO");
    }

    display.display();
    if (elapsed > 1000) {
      currentState = STATE_IDLE;
      lastEyeTime = millis();
    }
    return;
  }
  
  int currentAnim = animMode;
  if (lastActionKeyIndex == -2) {
    currentAnim = previewAnimOverride;
  } else if (lastActionKeyIndex >= 0 && lastActionKeyIndex < 8) {
    if (keyAnims[lastActionKeyIndex] != -1) {
      currentAnim = keyAnims[lastActionKeyIndex];
    }
  }
  
  String dispText = "";
  if (lastActionKeyIndex == -2) dispText = "PREVIEW";
  else if (lastActionKeyIndex >= 0 && lastActionKeyIndex < 8) {
    if (keyTexts[lastActionKeyIndex].length() > 0) dispText = keyTexts[lastActionKeyIndex];
    else {
      dispText = "F";
      dispText += (13 + lastActionKeyIndex);
      dispText += " HIT";
    }
  }

  auto printCentered = [](String text, int y, uint16_t c) {
    int sz = (text.length() > 10) ? 1 : 2;
    display.setTextSize(sz);
    display.setTextColor(c);
    int cw = sz * 6;
    int tw = text.length() * cw;
    int tx = (SCREEN_WIDTH - tw) / 2;
    if (tx < 0) tx = 0;
    int ty = y + (16 - (sz * 8)) / 2;
    display.setCursor(tx, ty);
    display.print(text);
  };
  
  if (currentAnim == 0) {
    int maxRadius = 40;
    int radius = (elapsed * maxRadius) / ACTION_DURATION;
    display.drawCircle(SCREEN_WIDTH/2, SCREEN_HEIGHT/2, radius, SSD1306_WHITE);
    if (radius > 5) display.drawCircle(SCREEN_WIDTH/2, SCREEN_HEIGHT/2, radius - 5, SSD1306_WHITE);
    
    if (lastActionKeyIndex == -1) {
      drawMicIcon(SCREEN_WIDTH/2, SCREEN_HEIGHT/2, SSD1306_WHITE, SSD1306_BLACK);
    } else {
      printCentered(dispText, 25, SSD1306_WHITE);
    }
    
  } else if (currentAnim == 1) {
    uint16_t color = ((elapsed / 100) % 2 == 0) ? SSD1306_BLACK : SSD1306_WHITE;
    uint16_t bg = ((elapsed / 100) % 2 == 0) ? SSD1306_WHITE : SSD1306_BLACK;
    
    if (bg == SSD1306_WHITE) {
      display.fillRect(10, 15, 108, 34, SSD1306_WHITE);
    } else {
      display.drawRect(10, 15, 108, 34, SSD1306_WHITE);
    }
    
    if (lastActionKeyIndex == -1) {
      drawMicIcon(SCREEN_WIDTH/2, SCREEN_HEIGHT/2, color, bg);
    } else {
      printCentered(dispText, 25, color);
    }
    
  } else if (currentAnim == 2) {
    if (lastActionKeyIndex == -1) {
      drawMicIcon(SCREEN_WIDTH/2, SCREEN_HEIGHT/2, SSD1306_WHITE, SSD1306_BLACK);
    } else {
      printCentered(dispText, 25, SSD1306_WHITE);
    }
  } else if (currentAnim == 3) {
    int maxRadius = 40;
    int radius = (elapsed * maxRadius) / ACTION_DURATION;
    display.drawCircle(SCREEN_WIDTH/2, SCREEN_HEIGHT/2, radius, SSD1306_WHITE);
    if (radius > 5) display.drawCircle(SCREEN_WIDTH/2, SCREEN_HEIGHT/2, radius - 5, SSD1306_WHITE);
    drawMicIcon(SCREEN_WIDTH/2, SCREEN_HEIGHT/2, SSD1306_WHITE, SSD1306_BLACK);
  }

  display.display();
  
  unsigned long duration = (currentAnim == 2) ? 800 : ACTION_DURATION;
  if (elapsed > duration) {
    currentState = STATE_IDLE;
    lastEyeTime = millis();
  }
}

void drawMenu() {
  display.clearDisplay();
  display.setTextSize(1);
  display.setTextColor(SSD1306_WHITE);
  display.setCursor(0, 0);
  display.println("-- SETTINGS MENU --");
  display.setCursor(0, 20);
  display.println("Set Brightness:");
  
  display.drawRect(10, 40, 100, 10, SSD1306_WHITE);
  int w = map(brightness, 0, 255, 0, 100);
  display.fillRect(10, 40, w, 10, SSD1306_WHITE);
  display.display();
}

void handleEncoderAction(bool forward) {
  if (!bleKeyboard.isConnected()) return;
  
  if (encMode == 0) { // Volume
    bleKeyboard.write(forward ? KEY_MEDIA_VOLUME_UP : KEY_MEDIA_VOLUME_DOWN);
  } else if (encMode == 1) { // Zoom (Ctrl + / Ctrl -)
    bleKeyboard.press(KEY_LEFT_CTRL);
    bleKeyboard.write(forward ? '+' : '-');
    bleKeyboard.releaseAll();
  } else if (encMode == 2) { // Browser Tabs
    bleKeyboard.press(KEY_LEFT_CTRL);
    if (!forward) bleKeyboard.press(KEY_LEFT_SHIFT);
    bleKeyboard.write(KEY_TAB);
    bleKeyboard.releaseAll();
  } else if (encMode == 3) { // Undo / Redo
    bleKeyboard.press(KEY_LEFT_CTRL);
    bleKeyboard.write(forward ? 'y' : 'z');
    bleKeyboard.releaseAll();
  } else if (encMode == 5) { // App Volume (F21 = left/down, F22 = right/up)
    bleKeyboard.write(forward ? KEY_F22 : KEY_F21);
  }
}


void setup() {
  Serial.begin(115200);
  loadConfig();
  
  Wire.begin();
  if(!display.begin(SSD1306_SWITCHCAPVCC, SCREEN_ADDRESS)) {
    Serial.println(F("SSD1306 allocation failed"));
  }
  
  display.ssd1306_command(SSD1306_SETCONTRAST);
  display.ssd1306_command(brightness);
  display.clearDisplay();
  display.display();
  
  eyes.begin(SCREEN_WIDTH, SCREEN_HEIGHT, 30);
  eyes.setAutoblinker(true, 2, 2);
  eyes.setIdleMode(true, 1, 2);
  
  bleKeyboard.begin();
  
  // Potentiometer setup
  analogReadResolution(12);          // 12-bit: 0-4095
  analogSetAttenuation(ADC_11db);    // Full 0-3.3V range
  // potLastPercent stays -1 so the loop initializes it on first read
  
  for(int i = 0; i < 8; i++) {
    switches[i].attach(SWITCH_PINS[i], INPUT_PULLUP);
    switches[i].interval(25);
    switches[i].setPressedState(LOW);
  }
}

void loop() {
  for(int i = 0; i < 8; i++) switches[i].update();
  
  if (currentState == STATE_IDLE || currentState == STATE_ACTION || currentState == STATE_EYES) {
    parseSerialData();
    
    for(int i = 0; i < 8; i++) {
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
    }
    
    // --- Dynamic Range Tracking ---
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
    }
    
    if (currentState == STATE_IDLE) {
      if (millis() - lastEyeTime > 20000) {
        currentState = STATE_EYES;
        eyeStateStartTime = millis();
        eyes.setMood(random(0, 4));
      } else {
        drawIdle();
      }
    } else if (currentState == STATE_ACTION) {
      drawAction();
    } else if (currentState == STATE_EYES) {
      eyes.update();
      if (millis() - eyeStateStartTime > 5000) {
        currentState = STATE_IDLE;
        lastEyeTime = millis();
      }
    }
  }
}
