import re
with open('src/main.cpp', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace ISR
old_isr_regex = r'// Interrupt para el encoder.*?lastInterruptTime = interruptTime;\n}'
new_isr = """// Interrupt para el encoder
const int8_t enc_states[] = {0,-1,1,0,1,0,0,-1,-1,0,0,1,0,1,-1,0};
volatile int encoderVal = 0;
uint8_t old_AB = 0;

void IRAM_ATTR readEncoder() {
  old_AB <<= 2;
  old_AB |= ( (digitalRead(ENCODER_CLK)<<1) | digitalRead(ENCODER_DT) );
  encoderVal += enc_states[(old_AB & 0x0f)];
  encoderSteps = encoderVal / 4; // KY-040 tiene 4 pasos por click
}"""
content = re.sub(old_isr_regex, new_isr, content, flags=re.DOTALL)

# Replace attachInterrupt
old_attach = "attachInterrupt(digitalPinToInterrupt(ENCODER_CLK), readEncoder, FALLING);"
new_attach = """attachInterrupt(digitalPinToInterrupt(ENCODER_CLK), readEncoder, CHANGE);
  attachInterrupt(digitalPinToInterrupt(ENCODER_DT), readEncoder, CHANGE);"""
content = content.replace(old_attach, new_attach)

with open('src/main.cpp', 'w', encoding='utf-8') as f:
    f.write(content)
print("Patch 7 applied.")
