#include <Arduino.h>
#include <BleKeyboard.h>
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include <Bounce2.h>
#include <Preferences.h>
#include "RoboEyes.h"
#include <WiFi.h>
#include <WiFiUdp.h>

const char* WIFI_SSID = "AIRCONECT_FIBRA-5865_5G";
const char* WIFI_PASSWORD = "ZnP8A6F53bMV[{I,";
WiFiUDP udp;

#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64
#define OLED_RESET    -1
#define SCREEN_ADDRESS 0x3C

Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);
RoboEyes<Adafruit_SSD1306> eyes(display);
BleKeyboard bleKeyboard("BindDeck", "Custom", 100);
Preferences preferences;

// Encoder
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
int currentIdleScreen = 0; // 0=Stats, 1=Time, 2=Eyes


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
  preferences.begin("binddeck", false);
  preferences.putInt("animMode", animMode);
  preferences.putInt("encMode", encMode);
  preferences.putInt("brightness", brightness);
  for(int i=0; i<8; i++) {
    char key[10];
    sprintf(key, "kbanim%d", i);
    preferences.putInt(key, keyAnims[i]);
  }
  preferences.end();
}


#include <time.h>

void drawTimeScreen() {
  display.clearDisplay();
  struct tm timeinfo;
  if (!getLocalTime(&timeinfo, 50)) {
    display.setCursor(20, 25);
    display.setTextSize(1);
    display.setTextColor(SSD1306_WHITE);
    display.print("Waiting for Time...");
    display.display();
    return;
  }
  
  char timeStringBuff[50];
  strftime(timeStringBuff, sizeof(timeStringBuff), "%H:%M", &timeinfo);
  
  display.setTextSize(3);
  display.setTextColor(SSD1306_WHITE);
  
  // Center time
  int16_t x1, y1;
  uint16_t w, h;
  display.getTextBounds(timeStringBuff, 0, 0, &x1, &y1, &w, &h);
  display.setCursor((128 - w) / 2, (64 - h) / 2);
  display.print(timeStringBuff);
  
  display.display();
}

// Forward declarations
void drawIdle();
void drawAction();
void drawMenu();
void drawUpdateScreen();
void drawMicIcon(int x, int y, uint16_t color, uint16_t bg);
void handleEncoderAction(bool forward);

void loadConfig() {
  preferences.begin("binddeck", true);
  animMode = preferences.getInt("animMode", 0);
  encMode = preferences.getInt("encMode", 0);
  brightness = preferences.getInt("brightness", 255);
  for(int i=0; i<8; i++) {
    char key[10];
    sprintf(key, "kbanim%d", i);
    keyAnims[i] = preferences.getInt(key, -1);
    
    sprintf(key, "kbtxt%d", i);
    keyTexts[i] = preferences.getString(key, "");
  }
  if (encMode < 0 || encMode > 5) encMode = 0;
  preferences.end();
}

// Track last time we received data (Serial or WiFi)
unsigned long lastDataTime = 0;

void processCommand(String data) {
    lastDataTime = millis();
    // Config commands from PC App (e.g. CFG:ANIM:1)
    if (data.startsWith("CFG:ANIM:")) {
      animMode = data.substring(9).toInt();
      saveConfig();
    } else if (data.startsWith("CFG:ENC:")) {
      encMode = data.substring(8).toInt();
      saveConfig();
    } else if (data.startsWith("CFG:BRIGHT:")) {
      brightness = data.substring(11).toInt();
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
        preferences.begin("binddeck", false);
        preferences.putString(pk, txt);
        preferences.end();
      }
    } else if (data.startsWith("CFG:WIFI:")) {
      String payload = data.substring(9);
      int pipeIdx = payload.indexOf('|');
      if (pipeIdx != -1) {
        String ssid = payload.substring(0, pipeIdx);
        String pwd = payload.substring(pipeIdx + 1);
        ssid.trim();
        pwd.trim();
        preferences.begin("binddeck", false);
        preferences.putString("wifiSSID", ssid);
        preferences.putString("wifiPwd", pwd);
        preferences.end();
        WiFi.disconnect(true, true);
        delay(100);
        WiFi.mode(WIFI_STA);
        WiFi.begin(ssid.c_str(), pwd.c_str());
  configTzTime("CET-1CEST,M3.5.0,M10.5.0/3", "pool.ntp.org");
      }
    } else if (data.startsWith("CMD:GET_WIFI")) {
      if (WiFi.status() == WL_CONNECTED) {
        preferences.begin("binddeck", true);
        String ssid = preferences.getString("wifiSSID", WIFI_SSID);
        preferences.end();
        Serial.print("WIFI_INFO:");
        Serial.print(ssid);
        Serial.print(",");
        Serial.println(WiFi.localIP().toString());
      } else {
        Serial.println("WIFI_INFO:DISCONNECTED,0.0.0.0");
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

void parseSerialData() {
  if (Serial.available()) {
    String data = Serial.readStringUntil('\n');
    data.trim();
    if (data.length() > 0) {
      processCommand(data);
    }
  }
}

// Batery config
const int BATTERY_PIN = 35; // Pin analogico para medir voltaje

int getBatteryPercentage() {
  // Con un divisor de voltaje (100k + 100k), el voltaje en el pin es la mitad de la bateria.
  // Bateria max = 4.2V -> Pin = 2.1V.
  // En el ESP32, 2.1V es aprox 2600-2800 en el ADC de 12 bits (0-4095).
  // Estos valores deben ajustarse en base al divisor real que uses.
  int raw = analogRead(BATTERY_PIN);
  
  // Si el pin no está conectado al divisor, leerá un valor muy bajo (ruido o 0)
  // Una batería agotada (3.0V) seguiría dando > 1800. Así que si es menor a 1000, 
  // sabemos seguro que no hay hardware de medición conectado.
  if (raw < 1000) {
    return -1; // -1 significa "Batería no detectada"
  }
  
  // Asumiendo lectura de 0 a 4095. Para 4.2V (100%), leemos aprox 2600. Para 3.3V (0%), leemos aprox 2050.
  // IMPORTANTE: Ajustar estos valores experimentalmente con un polímetro.
  int minRaw = 2050; // 3.3V
  int maxRaw = 2600; // 4.2V
  
  int pct = map(raw, minRaw, maxRaw, 0, 100);
  return constrain(pct, 0, 100);
}

void drawBatteryIcon(int x, int y, int percentage) {
  // Draw percentage text to the left of the icon
  display.setCursor(x, y + 1);
  display.print(percentage);
  display.print("%");
  
  // Icon offset
  int iconX = x + 25; // 4 chars * 6px = 24px + 1px gap
  
  // Draw battery outline
  display.drawRect(iconX, y, 20, 10, SSD1306_WHITE);
  display.fillRect(iconX + 20, y + 2, 2, 6, SSD1306_WHITE); // Battery tip
  
  // Draw fill
  int fillWidth = map(percentage, 0, 100, 0, 16);
  if (fillWidth > 0) {
    display.fillRect(iconX + 2, y + 2, fillWidth, 6, SSD1306_WHITE);
  }
}

void drawWiFiIcon(int x, int y) {
  // Simple Wi-Fi waves
  display.drawPixel(x+4, y+6, SSD1306_WHITE);
  display.drawLine(x+2, y+4, x+6, y+4, SSD1306_WHITE);
  display.drawLine(x, y+2, x+8, y+2, SSD1306_WHITE);
}

void drawBTIcon(int x, int y) {
  display.drawLine(x+3, y, x+3, y+8, SSD1306_WHITE);
  display.drawLine(x+3, y, x+5, y+2, SSD1306_WHITE);
  display.drawLine(x+5, y+2, x+1, y+6, SSD1306_WHITE);
  display.drawLine(x+3, y+8, x+5, y+6, SSD1306_WHITE);
  display.drawLine(x+5, y+6, x+1, y+2, SSD1306_WHITE);
}

void drawIdle() {
  display.clearDisplay();

  // Si no hemos recibido datos (ni por USB ni por WiFi) en 3 segundos,
  // asumimos que no hay PC conectado o hay problemas de conexion
  bool isDisconnected = (millis() - lastDataTime > 3000);

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
      display.display();
      return;
    }
  }
  
  display.setTextSize(1);
  display.setTextColor(SSD1306_WHITE);
  
  // Header
  display.setCursor(28, 0);
  if (isDisconnected) {
      display.setCursor(20, 0);
      display.print("NO SIGNAL");
  } else {
      display.print("PC STATS");
  }
  
  // Connection Icons (Bottom Right)
  if (WiFi.status() == WL_CONNECTED) {
    drawWiFiIcon(116, 54);
  } else {
    drawBTIcon(120, 54);
  }
  
  int batPct = getBatteryPercentage();
  if (batPct != -1) {
      drawBatteryIcon(80, 0, batPct);
      if (bleKeyboard.isConnected()) {
          bleKeyboard.setBatteryLevel(batPct);
      }
  }
  
  // Data
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

void drawUpdateScreen() {
  int frame = 0;
  while(true) {
    display.clearDisplay();
    
    // Textos
    display.setTextSize(1);
    display.setTextColor(SSD1306_WHITE);
    
    display.setCursor(20, 35);
    display.println("Actualizando...");
    
    display.setCursor(16, 45);
    display.println("No desconecte el");
    
    display.setCursor(31, 55);
    display.println("dispositivo");
    
    // Spinner
    int cx = 64;
    int cy = 16;
    int r = 10;
    
    for (int i = 0; i < 8; i++) {
      float angle = (i * 45) * 3.14159 / 180.0;
      int x = cx + cos(angle) * r;
      int y = cy + sin(angle) * r;
      
      // Calculate dot size based on frame to create rotation effect
      int dotDistance = (i - (frame % 8) + 8) % 8;
      
      if (dotDistance < 2) {
        display.fillCircle(x, y, 2, SSD1306_WHITE); // Big dot
      } else if (dotDistance < 4) {
        display.drawCircle(x, y, 1, SSD1306_WHITE); // Medium dot
      } else {
        display.drawPixel(x, y, SSD1306_WHITE); // Small dot
      }
    }
    
    display.display();
    frame++;
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
    if (encMode == 0 || encMode == 5) {
      display.setCursor(encMode == 0 ? 46 : 40, 15);
      display.print(encMode == 0 ? "VOLUME" : "APP VOL");
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
  if (encMode == 0) { // Volume
    if (bleKeyboard.isConnected()) bleKeyboard.write(forward ? KEY_MEDIA_VOLUME_UP : KEY_MEDIA_VOLUME_DOWN);
    Serial.println(forward ? "ENC:VUP" : "ENC:VDN");
  } else if (encMode == 1) { // Zoom (Ctrl + / Ctrl -)
    if (bleKeyboard.isConnected()) {
      bleKeyboard.press(KEY_LEFT_CTRL);
      bleKeyboard.write(forward ? '+' : '-');
      bleKeyboard.releaseAll();
    }
    Serial.println(forward ? "ENC:ZIN" : "ENC:ZOUT");
  } else if (encMode == 2) { // Browser Tabs
    if (bleKeyboard.isConnected()) {
      bleKeyboard.press(KEY_LEFT_CTRL);
      if (!forward) bleKeyboard.press(KEY_LEFT_SHIFT);
      bleKeyboard.write(KEY_TAB);
      bleKeyboard.releaseAll();
    }
    Serial.println(forward ? "ENC:TFWD" : "ENC:TBCK");
  } else if (encMode == 3) { // Undo / Redo
    if (bleKeyboard.isConnected()) {
      bleKeyboard.press(KEY_LEFT_CTRL);
      bleKeyboard.write(forward ? 'y' : 'z');
      bleKeyboard.releaseAll();
    }
    Serial.println(forward ? "ENC:REDO" : "ENC:UNDO");
  } else if (encMode == 5) { // App Volume
    if (bleKeyboard.isConnected()) bleKeyboard.write(forward ? KEY_F24 : KEY_F23);
    Serial.println(forward ? "ENC:APPVUP" : "ENC:APPVDN");
  }
}

void setupWiFi() {
  preferences.begin("binddeck", true);
  String ssid = preferences.getString("wifiSSID", WIFI_SSID);
  String pwd = preferences.getString("wifiPwd", WIFI_PASSWORD);
  preferences.end();
  
  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid.c_str(), pwd.c_str());
  configTzTime("CET-1CEST,M3.5.0,M10.5.0/3", "pool.ntp.org");
}

void loopWiFi() {
  if (WiFi.status() == WL_CONNECTED) {
    static bool udpStarted = false;
    if (!udpStarted) {
      udp.begin(4210);
      udpStarted = true;
    }
    
    int packetSize = udp.parsePacket();
    if (packetSize) {
      char packetBuffer[255];
      int len = udp.read(packetBuffer, 255);
      if (len > 0) {
        packetBuffer[len] = 0;
        String data = String(packetBuffer);
        data.trim();
        if (data.length() > 0) {
           processCommand(data);
        }
      }
    }
  }
}

void setup() {
  Serial.begin(115200);
  Serial.setTimeout(10);
  loadConfig();
  
  setupWiFi();
  
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
  
  // Encoder setup
  pinMode(ENCODER_CLK, INPUT_PULLUP);
  pinMode(ENCODER_DT, INPUT_PULLUP);
  pinMode(ENCODER_SW, INPUT_PULLUP);
  attachInterrupt(digitalPinToInterrupt(ENCODER_CLK), readEncoder, CHANGE);
  attachInterrupt(digitalPinToInterrupt(ENCODER_DT), readEncoder, CHANGE);
  
  for(int i = 0; i < 8; i++) {
    switches[i].attach(SWITCH_PINS[i], INPUT_PULLUP);
    switches[i].interval(25);
    switches[i].setPressedState(LOW);
  }
  
  menuBtn.attach(4, INPUT_PULLUP);
  menuBtn.interval(25);
  menuBtn.setPressedState(LOW);
}

void loop() {
  for(int i = 0; i < 8; i++) switches[i].update();
  menuBtn.update();
  
  if (menuBtn.pressed()) {
    currentIdleScreen = (currentIdleScreen + 1) % 3;
    if (currentIdleScreen == 2) {
       currentState = STATE_EYES;
       eyes.setMood(random(0, 4));
       eyeStateStartTime = millis();
    } else {
       currentState = STATE_IDLE;
    }
  }

  
  if (currentState == STATE_IDLE || currentState == STATE_ACTION || currentState == STATE_EYES) {
    parseSerialData();
    loopWiFi();
    
    for(int i = 0; i < 8; i++) {
      if(switches[i].pressed()) {
        if(bleKeyboard.isConnected()) {
          bleKeyboard.press(MACRO_KEYS[i]);
          delay(10);
          bleKeyboard.releaseAll();
        }
        Serial.println("BTN:" + String(i));
        lastActionKeyIndex = i;
        currentState = STATE_ACTION;
        actionStartTime = millis();
      }
    }
    
    // --- Encoder Button (Programmable) ---
    static unsigned long lastEncoderButtonPress = 0;
    if (digitalRead(ENCODER_SW) == LOW) {
      if (millis() - lastEncoderButtonPress > 200) {
        if (bleKeyboard.isConnected()) {
          bleKeyboard.press(KEY_F21);
          delay(10);
          bleKeyboard.releaseAll();
        }
        Serial.println("BTN:8");
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
        
        if (encMode == 0 || encMode == 5) {
           visualVolume += forward ? 4 : -4;
           if (visualVolume < 0) visualVolume = 0;
           if (visualVolume > 100) visualVolume = 100;
        }
      }
      
      lastEncoderSteps = currentSteps;
      lastActionKeyIndex = -3;
      currentState = STATE_ACTION;
      actionStartTime = millis();
    }
    
    if (currentState == STATE_IDLE) {
      if (currentIdleScreen == 0) {
        drawIdle(); // PC Stats
      } else if (currentIdleScreen == 1) {
        drawTimeScreen();
      }
    } else if (currentState == STATE_ACTION) {
      drawAction();
    } else if (currentState == STATE_EYES) {
      eyes.update();
      // Change mood randomly
      if (millis() - eyeStateStartTime > 4000) {
        eyes.setMood(random(0, 4));
        eyeStateStartTime = millis();
      }
    }
  }
}
