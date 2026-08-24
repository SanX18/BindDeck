import re

# Update pc_monitor.py
with open('pc_script/pc_monitor.py', 'r', encoding='utf-8') as f:
    pc = f.read()

pc = pc.replace("range(13, 21)", "range(13, 22)")
with open('pc_script/pc_monitor.py', 'w', encoding='utf-8') as f:
    f.write(pc)

# Update index.html
with open('pc_script/templates/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

html = html.replace('<div class="encoder-mock" id="encoder-knob" style="cursor: grab;"></div>',
                    '<div class="encoder-mock keycap" id="encoder-knob" data-key="21" style="cursor: pointer; display: flex; align-items: center; justify-content: center; font-size: 12px; color: white; font-weight: bold;">ENC</div>')

with open('pc_script/templates/index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("PC App patched.")
