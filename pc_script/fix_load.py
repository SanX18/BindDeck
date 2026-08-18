import codecs
import re

js = codecs.open('static/app.js', 'r', 'utf-8').read()

target = "document.getElementById('globalLedColor').value = config.esp32.ledColor;"
replacement = "document.getElementById('globalLedColor').value = config.esp32.ledColor;\n            }\n            if (typeof toggleCustomAnim === 'function') toggleCustomAnim();"

if target in js and "toggleCustomAnim();" not in js:
    js = js.replace(target, replacement)
    codecs.open('static/app.js', 'w', 'utf-8').write(js)
    print("Fixed toggle on load")
