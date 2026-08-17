#include <Arduino.h>
#include <BleKeyboard.h>
#include <ESP32Encoder.h>
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include <Bounce2.h>
#include <Preferences.h>

#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64
#define OLED_RESET    -1
#define SCREEN_ADDRESS 0x3C

Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);
BleKeyboard bleKeyboard("Macro Deck", "Custom", 100);
ESP32Encoder encoder;
Preferences preferences;

long oldPosition = 0;

// Pins
const int SWITCH_PINS[8] = {13, 12, 14, 27, 26, 25, 33, 32};
const uint8_t MACRO_KEYS[8] = {KEY_F13, KEY_F14, KEY_F15, KEY_F16, KEY_F17, KEY_F18, KEY_F19, KEY_F20};
Bounce2::Button switches[8];

const int ENCODER_BTN_PIN = 23;
Bounce2::Button encoderBtn;

enum State {
  STATE_IDLE,
  STATE_ACTION,
  STATE_MENU
};
State currentState = STATE_IDLE;

// Telemetry Data
int cpu_temp = 0, cpu_usage = 0, gpu_temp = 0, gpu_usage = 0;

// Action Data
unsigned long actionStartTime = 0;
const unsigned long ACTION_DURATION = 800;
int lastActionKeyIndex = -1; // -1: mute

// Config Data
int brightness = 255;
int animMode = 0; // 0: Circles, 1: Flash, 2: Minimal
int encMode = 0;  // 0: Volume, 1: Vertical Arrows, 2: Horizontal Arrows

void saveConfig() {
  preferences.begin("macrodeck", false);
  preferences.putInt("animMode", animMode);
  preferences.putInt("encMode", encMode);
  preferences.putInt("brightness", brightness);
  preferences.end();
}

void loadConfig() {
  preferences.begin("macrodeck", true);
  animMode = preferences.getInt("animMode", 0);
  encMode = preferences.getInt("encMode", 0);
  brightness = preferences.getInt("brightness", 255);
  preferences.end();
}

void parseSerialData() {
  if (Serial.available() > 0) {
    String data = Serial.readStringUntil('\n');
    data.trim();
    
    // Config commands from PC App (e.g. CFG:ANIM:1)
    if (data.startsWith("CFG:")) {
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
      }
      return;
    }
    
    // Telemetry: C:45,U:10,G:60,V:50
    if (data.indexOf("C:") != -1 && data.indexOf("G:") != -1) {
      sscanf(data.c_str(), "C:%d,U:%d,G:%d,V:%d", &cpu_temp, &cpu_usage, &gpu_temp, &gpu_usage);
    }
  }
}

void drawIdle() {
  display.clearDisplay();
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
  
  display.display();
}

void drawAction() {
  display.clearDisplay();
  unsigned long elapsed = millis() - actionStartTime;
  
  if (animMode == 0) {
    // Mode 0: Expanding Circles
    int maxRadius = 40;
    int radius = (elapsed * maxRadius) / ACTION_DURATION;
    display.drawCircle(SCREEN_WIDTH/2, SCREEN_HEIGHT/2, radius, SSD1306_WHITE);
    if (radius > 5) display.drawCircle(SCREEN_WIDTH/2, SCREEN_HEIGHT/2, radius - 5, SSD1306_WHITE);
    
    display.setTextSize(2);
    display.setTextColor(SSD1306_WHITE);
    if (lastActionKeyIndex == -1) {
      display.setCursor(20, 25); display.print("  MUTE  ");
    } else {
      display.setCursor(15, 25); display.print(" KEY F"); display.print(13 + lastActionKeyIndex);
    }
    
  } else if (animMode == 1) {
    // Mode 1: Flashing Box
    if ((elapsed / 100) % 2 == 0) {
      display.fillRect(10, 15, 108, 34, SSD1306_WHITE);
      display.setTextColor(SSD1306_BLACK);
    } else {
      display.drawRect(10, 15, 108, 34, SSD1306_WHITE);
      display.setTextColor(SSD1306_WHITE);
    }
    display.setTextSize(2);
    if (lastActionKeyIndex == -1) {
      display.setCursor(25, 25); display.print(" MUTE ");
    } else {
      display.setCursor(20, 25); display.print("KEY F"); display.print(13 + lastActionKeyIndex);
    }
    
  } else if (animMode == 2) {
    // Mode 2: Minimalist, just fast text (ends faster)
    display.setTextSize(2);
    display.setTextColor(SSD1306_WHITE);
    if (lastActionKeyIndex == -1) {
      display.setCursor(40, 25); display.print("MUTE");
    } else {
      display.setCursor(25, 25); display.print("F"); display.print(13 + lastActionKeyIndex); display.print(" HIT");
    }
  }

  display.display();
  
  unsigned long duration = (animMode == 2) ? 400 : ACTION_DURATION;
  if (elapsed > duration) {
    currentState = STATE_IDLE;
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
  } else if (encMode == 1) { // Up/Down Arrows
    bleKeyboard.write(forward ? KEY_DOWN_ARROW : KEY_UP_ARROW);
  } else if (encMode == 2) { // Left/Right Arrows
    bleKeyboard.write(forward ? KEY_RIGHT_ARROW : KEY_LEFT_ARROW);
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
  
  bleKeyboard.begin();
  
  ESP32Encoder::useInternalWeakPullResistors = UP;
  encoder.attachHalfQuad(18, 19);
  encoder.setCount(0);
  
  encoderBtn.attach(ENCODER_BTN_PIN, INPUT_PULLUP);
  encoderBtn.interval(25);
  encoderBtn.setPressedState(LOW);
  
  for(int i = 0; i < 8; i++) {
    switches[i].attach(SWITCH_PINS[i], INPUT_PULLUP);
    switches[i].interval(25);
    switches[i].setPressedState(LOW);
  }
}

void loop() {
  encoderBtn.update();
  for(int i = 0; i < 8; i++) switches[i].update();
  
  if (currentState == STATE_IDLE || currentState == STATE_ACTION) {
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
    
    long newPosition = encoder.getCount() / 2;
    if (newPosition != oldPosition) {
      handleEncoderAction(newPosition > oldPosition);
      oldPosition = newPosition;
    }
    
    if (encoderBtn.pressed()) {
      unsigned long pressedTime = millis();
      bool longPress = false;
      while(!encoderBtn.released() && millis() - pressedTime < 1000) {
        encoderBtn.update();
        delay(10);
      }
      
      if (millis() - pressedTime >= 1000) {
        longPress = true;
      }
      
      if (longPress) {
        currentState = STATE_MENU;
        encoder.setCount(brightness);
        oldPosition = brightness;
      } else {
        if(bleKeyboard.isConnected()) {
          bleKeyboard.write(KEY_MEDIA_MUTE);
        }
        lastActionKeyIndex = -1;
        currentState = STATE_ACTION;
        actionStartTime = millis();
      }
    }
    
    if (currentState == STATE_IDLE) {
      drawIdle();
    } else if (currentState == STATE_ACTION) {
      drawAction();
    }
    
  } else if (currentState == STATE_MENU) {
    long newPosition = encoder.getCount();
    if (newPosition != oldPosition) {
      brightness = constrain(newPosition, 0, 255);
      encoder.setCount(brightness);
      oldPosition = brightness;
      display.ssd1306_command(SSD1306_SETCONTRAST);
      display.ssd1306_command(brightness);
    }
    
    if (encoderBtn.pressed()) {
      saveConfig();
      encoder.setCount(0);
      oldPosition = 0;
      currentState = STATE_IDLE;
    }
    
    drawMenu();
  }
}
