import re

with open('src/main.cpp', 'r', encoding='utf-8') as f:
    content = f.read()

# Add Menu Button object
menu_btn_def = """Bounce2::Button switches[8];
Bounce2::Button menuBtn;
int currentIdleScreen = 0; // 0=Stats, 1=Time, 2=Eyes
"""
content = content.replace("Bounce2::Button switches[8];", menu_btn_def)

# Add NTP include and time screen draw function
ntp_and_time = """
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
"""
content = content.replace("// Forward declarations", ntp_and_time + "\n// Forward declarations")

# Add NTP init
setup_wifi = """WiFi.begin(ssid.c_str(), pwd.c_str());
  configTzTime("CET-1CEST,M3.5.0,M10.5.0/3", "pool.ntp.org");"""
content = content.replace("WiFi.begin(ssid.c_str(), pwd.c_str());", setup_wifi)

# Attach Menu Button in setup
setup_attach = """switches[i].interval(25);
    switches[i].setPressedState(LOW);
  }
  
  menuBtn.attach(4, INPUT_PULLUP);
  menuBtn.interval(25);
  menuBtn.setPressedState(LOW);"""
content = content.replace("""switches[i].interval(25);
    switches[i].setPressedState(LOW);
  }""", setup_attach)

# Handle menu button in loop
loop_start = """void loop() {
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
"""
content = content.replace("""void loop() {
  for(int i = 0; i < 8; i++) switches[i].update();""", loop_start)


# Update IDLE logic
old_idle = """    if (currentState == STATE_IDLE) {
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
    }"""
    
new_idle = """    if (currentState == STATE_IDLE) {
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
    }"""
content = content.replace(old_idle, new_idle)

with open('src/main.cpp', 'w', encoding='utf-8') as f:
    f.write(content)

print("Patch applied.")
