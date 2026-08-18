import re
import codecs

html = codecs.open('templates/index.html', 'r', 'utf-8').read()

replacement = '''<select id="keyAnim">
                    <option value="-1" data-i18n="anim_default">Default (from Device Settings)</option>
                    <option value="0" data-i18n="anim_0">Expanding Waves</option>
                    <option value="1" data-i18n="anim_1">Flash Notification</option>
                    <option value="2" data-i18n="anim_2">Minimal Text</option>
                    <option value="3" data-i18n="anim_3">Waves + Mic Mute</option>
                    <option value="4" data-i18n="anim_4">Imagen Personalizada (.h)</option>
                </select>'''

pattern = r'<select id="keyAnim">.*?</select>'
if re.search(pattern, html, flags=re.DOTALL):
    html = re.sub(pattern, replacement, html, flags=re.DOTALL)
    codecs.open('templates/index.html', 'w', 'utf-8').write(html)
    print("keyAnim updated via Regex")
else:
    print("keyAnim still not found!")
