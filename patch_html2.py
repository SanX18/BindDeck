with open('pc_script/templates/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

old_div = '<div class="encoder-mock keycap" id="encoder-knob" data-key="21" style="cursor: pointer; display: flex; align-items: center; justify-content: center; font-size: 12px; color: white; font-weight: bold;">ENC</div>'
new_div = '<div class="encoder-mock keycap" id="encoder-knob" data-key="21" style="cursor: pointer; display: flex; align-items: center; justify-content: center; font-size: 12px; color: white; font-weight: bold; border-radius: 50% !important; width: 60px !important; height: 60px !important;">ENC</div>'

html = html.replace(old_div, new_div)

with open('pc_script/templates/index.html', 'w', encoding='utf-8') as f:
    f.write(html)
