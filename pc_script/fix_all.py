import codecs
import re

# 1. Fix endpoints in pc_monitor.py
py = codecs.open('pc_monitor.py', 'r', 'utf-8').read()

flash_endpoint = '''
@app.route('/api/flash', methods=['POST'])
def api_flash():
    import time
    try:
        # Simulate flash
        time.sleep(2)
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/upload_anim', methods=['POST'])
def upload_anim():
    if 'file' not in request.files:
        return jsonify({"success": False, "error": "No file part"})
    file = request.files['file']
    if file.filename == '':
        return jsonify({"success": False, "error": "No selected file"})
    if file:
        try:
            return jsonify({"success": True})
        except Exception as e:
            return jsonify({"success": False, "error": str(e)})
'''

if '/api/flash' not in py:
    py = py.replace('if __name__ == "__main__":', flash_endpoint + '\nif __name__ == "__main__":')
    codecs.open('pc_monitor.py', 'w', 'utf-8').write(py)
    print("Endpoints added to pc_monitor.py")

# 2. Add option 4 to keyAnim in index.html
html = codecs.open('templates/index.html', 'r', 'utf-8').read()

target = '''<select id="keyAnim">
                    <option value="-1" data-i18n="anim_default">Default (from Device Settings)</option>
                    <option value="0" data-i18n="anim_0">Expanding Waves</option>
                    <option value="1" data-i18n="anim_1">Flash Notification</option>
                    <option value="2" data-i18n="anim_2">Minimal Text</option>
                    <option value="3" data-i18n="anim_3">Waves + Mic Mute</option>
                </select>'''

replacement = '''<select id="keyAnim">
                    <option value="-1" data-i18n="anim_default">Default (from Device Settings)</option>
                    <option value="0" data-i18n="anim_0">Expanding Waves</option>
                    <option value="1" data-i18n="anim_1">Flash Notification</option>
                    <option value="2" data-i18n="anim_2">Minimal Text</option>
                    <option value="3" data-i18n="anim_3">Waves + Mic Mute</option>
                    <option value="4" data-i18n="anim_4">Imagen Personalizada (.h)</option>
                </select>'''

if target in html:
    html = html.replace(target, replacement)
    codecs.open('templates/index.html', 'w', 'utf-8').write(html)
    print("keyAnim updated in index.html")
else:
    print("keyAnim target not found!")

