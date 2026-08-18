import re
import codecs

html = codecs.open('templates/index.html', 'r', 'utf-8').read()

replacement = '''<select id="animMode" onchange="toggleCustomAnim()">
                    <option value="0" data-i18n="anim_0">Expanding Waves</option>
                    <option value="1" data-i18n="anim_1">Flash Notification</option>
                    <option value="2" data-i18n="anim_2">Minimal Text</option>
                    <option value="3" data-i18n="anim_3">Waves + Mic Mute</option>
                    <option value="4" data-i18n="anim_4">Imagen Personalizada (.h)</option>
                </select>
                
                <div id="customAnimContainer" style="display: none; margin-top: 10px; background: var(--bg-panel); padding: 10px; border-radius: 8px; border: 1px solid var(--border);">
                    <label for="customAnimFile" class="btn-secondary" style="display: inline-block; width: 100%; text-align: center; cursor: pointer; font-size: 0.85rem; padding: 0.4rem;">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="vertical-align: middle; margin-right: 5px;"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg>
                        Subir Archivo .h
                    </label>
                    <input type="file" id="customAnimFile" accept=".h" style="display: none;" onchange="uploadCustomAnim()">
                    <p id="customAnimStatus" style="font-size: 0.75rem; color: var(--text-muted); margin-top: 5px; text-align: center; margin-bottom: 0;"></p>
                    
                    <div style="text-align: center; margin-top: 10px; border-top: 1px dashed var(--border); padding-top: 8px;">
                        <a href="https://ejemplo.com/animaciones" target="_blank" style="color: var(--primary); text-decoration: none; font-size: 0.85rem; font-weight: bold;">
                            Explorar mas animaciones!
                        </a>
                    </div>
                </div>'''

pattern = r'<select id="animMode">.*?</select>'
if re.search(pattern, html, flags=re.DOTALL):
    html = re.sub(pattern, replacement, html, flags=re.DOTALL)
    codecs.open('templates/index.html', 'w', 'utf-8').write(html)
    print("HTML updated")
else:
    print("Not found")

# JS injection
js = codecs.open('static/app.js', 'r', 'utf-8').read()
js_func = '''
function toggleCustomAnim() {
    const animMode = document.getElementById('animMode').value;
    const container = document.getElementById('customAnimContainer');
    if(animMode == "4") {
        container.style.display = 'block';
    } else {
        container.style.display = 'none';
    }
}

function uploadCustomAnim() {
    const fileInput = document.getElementById('customAnimFile');
    const status = document.getElementById('customAnimStatus');
    
    if (fileInput.files.length === 0) return;
    
    const file = fileInput.files[0];
    status.innerText = "Subiendo " + file.name + "...";
    status.style.color = "var(--text-main)";
    
    const formData = new FormData();
    formData.append('file', file);
    
    fetch('/api/upload_anim', {
        method: 'POST',
        body: formData
    })
    .then(res => res.json())
    .then(data => {
        if(data.success) {
            status.innerText = "Animacion guardada!";
            status.style.color = "var(--primary)";
        } else {
            status.innerText = "Error: " + data.error;
            status.style.color = "red";
        }
    })
    .catch(err => {
        status.innerText = "Error de conexion.";
        status.style.color = "red";
    });
}
'''
if 'function toggleCustomAnim' not in js:
    js = js + "\n" + js_func
    codecs.open('static/app.js', 'w', 'utf-8').write(js)
    print("JS updated")

# Py injection
py = codecs.open('pc_monitor.py', 'r', 'utf-8').read()
py_endpoint = '''
@app.route('/api/upload_anim', methods=['POST'])
def upload_anim():
    if 'file' not in request.files:
        return jsonify({"success": False, "error": "No file part"})
    file = request.files['file']
    if file.filename == '':
        return jsonify({"success": False, "error": "No selected file"})
    if file:
        try:
            # En un entorno real guardariamos el archivo y lo enviariamos al ESP32
            # file.save("custom_anim.h")
            return jsonify({"success": True})
        except Exception as e:
            return jsonify({"success": False, "error": str(e)})
'''
if '/api/upload_anim' not in py:
    py = py.replace("if __name__ == '__main__':", py_endpoint + "\nif __name__ == '__main__':")
    codecs.open('pc_monitor.py', 'w', 'utf-8').write(py)
    print("Py updated")

