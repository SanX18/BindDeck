import re

with open('src/main.cpp', 'r', encoding='utf-8') as f:
    c = f.read()

pot_vars = r'// Potentiometer.*?unsigned long lastPotChange = 0;'
enc_vars = """#define ENCODER_CLK 18
#define ENCODER_DT 19
#define ENCODER_SW 5"""
c = re.sub(pot_vars, enc_vars, c, flags=re.DOTALL)

with open('src/main.cpp', 'w', encoding='utf-8') as f:
    f.write(c)
