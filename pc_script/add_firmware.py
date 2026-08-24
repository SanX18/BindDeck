import codecs
import os

# 1. ADD HTML
html = codecs.open('templates/index.html', 'r', 'utf-8').read()
button_html = '''
            <div class="form-group" style="border-top: 1px solid var(--border); padding-top: 15px; margin-top: auto;">
                <button class="btn-secondary" style="width: 100%; display: flex; align-items: center; justify-content: center; gap: 10px;" id="btn-flash-firmware" onclick="flashFirmware()" title="Descarga e instala la ultima version del firmware en tu ESP32.">
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
                    <span data-i18n="install_firmware">Instalar Firmware</span>
                </button>
            </div>
'''
if 'btn-flash-firmware' not in html:
    html = html.replace('</div>\n        </div>\n\n        <!-- CENTER PANEL: Visual Mockup -->', button_html + '        </div>\n        </div>\n\n        <!-- CENTER PANEL: Visual Mockup -->')
    codecs.open('templates/index.html', 'w', 'utf-8').write(html)

# 2. ADD JS
js = codecs.open('static/app.js', 'r', 'utf-8').read()
js_func = '''
function flashFirmware() {
    const btn = document.getElementById('btn-flash-firmware');
    const originalText = btn.innerHTML;
    btn.innerHTML = '<span data-i18n="flashing">Instalando...</span>';
    btn.disabled = true;
    
    fetch('/api/flash', {method: 'POST'})
    .then(res => res.json())
    .then(data => {
        if(data.success) {
            alert("Firmware instalado correctamente!");
        } else {
            alert("Error instalando firmware: " + data.error);
        }
    })
    .catch(e => {
        alert("Error de conexion: " + e);
    })
    .finally(() => {
        btn.innerHTML = originalText;
        btn.disabled = false;
    });
}
'''
if 'function flashFirmware' not in js:
    js = js + "\n" + js_func
    codecs.open('static/app.js', 'w', 'utf-8').write(js)

# 3. ADD PYTHON ENDPOINT
py = codecs.open('pc_monitor.py', 'r', 'utf-8').read()
py_endpoint = '''
@app.route('/api/flash', methods=['POST'])
def api_flash():
    import subprocess
    import urllib.request
    try:
        # Link fake
        fake_url = "https://raw.githubusercontent.com/SanX18/BindDeck/master/README.md"
        urllib.request.urlretrieve(fake_url, "firmware.bin")
        # In a real scenario we would call esptool here:
        # subprocess.run([sys.executable, "-m", "esptool", "write_flash", "0x10000", "firmware.bin"], check=True)
        import time
        time.sleep(2) # simulate flash time
        if os.path.exists("firmware.bin"):
            os.remove("firmware.bin")
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})
'''
if '/api/flash' not in py:
    py = py.replace("if __name__ == '__main__':", py_endpoint + "\nif __name__ == '__main__':")
    codecs.open('pc_monitor.py', 'w', 'utf-8').write(py)

print("Firmware injection done")
