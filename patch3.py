import re
with open('src/main.cpp', 'r', encoding='utf-8') as f:
    content = f.read()

content = re.sub(r'// Switch Slider\n#define SWITCH_SLIDER 18\nbool lastSliderState = false;\n', '', content)
content = re.sub(r'\s*pinMode\(SWITCH_SLIDER, INPUT_PULLUP\);\n', '', content)
content = re.sub(r'\s*// --- Switch Slider \(Play/Pause\) ---.*?delay\(50\);\n\s*}', '', content, flags=re.DOTALL)

with open('src/main.cpp', 'w', encoding='utf-8') as f:
    f.write(content)
print("Switch code removed.")
