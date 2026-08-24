import re
with open('src/main.cpp', 'r', encoding='utf-8') as f:
    content = f.read()

# Change pins
content = re.sub(r'#define ENCODER_CLK 16', '#define ENCODER_CLK 18', content)
content = re.sub(r'#define ENCODER_DT  17', '#define ENCODER_DT  19', content)

# Better encoder ISR
new_isr = """// Interrupt para el encoder
void IRAM_ATTR readEncoder() {
  static unsigned long lastInterruptTime = 0;
  unsigned long interruptTime = millis();
  if (interruptTime - lastInterruptTime > 2) { // 2ms debounce
    int dtValue = digitalRead(ENCODER_DT);
    if (dtValue == HIGH) {
      encoderSteps++;
    } else {
      encoderSteps--;
    }
  }
  lastInterruptTime = interruptTime;
}"""
content = re.sub(r'// Interrupt para el encoder.*?}\n', new_isr + '\n', content, flags=re.DOTALL)

# Better loop handling
old_loop = """    // --- Rotary Encoder ---
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
    }"""

new_loop = """    // --- Rotary Encoder ---
    if (encoderSteps != lastEncoderSteps) {
      noInterrupts();
      int currentSteps = encoderSteps;
      interrupts();
      
      int diff = currentSteps - lastEncoderSteps;
      
      for(int i = 0; i < abs(diff); i++) {
        bool forward = (diff > 0);
        handleEncoderAction(forward);
        
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
content = content.replace(old_loop, new_loop)

with open('src/main.cpp', 'w', encoding='utf-8') as f:
    f.write(content)
print("Patch 4 applied.")
