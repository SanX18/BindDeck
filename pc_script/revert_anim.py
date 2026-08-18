import codecs

# Read the file
html = codecs.open('templates/index.html', 'r', 'utf-8').read()

# Fix the duplicate block that replace_file_content messed up.
# Actually, the easiest way to reset the file is to grab origin/master, and THEN patch in the firmware button.
import os
os.system('git restore templates/index.html')
html = codecs.open('templates/index.html', 'r', 'utf-8').read()

firmware_btn = '''
            <div class="form-group" style="border-top: 1px solid var(--border); padding-top: 15px; margin-top: auto;">
                <button class="btn-secondary" style="width: 100%; display: flex; align-items: center; justify-content: center; gap: 10px;" id="btn-flash-firmware" onclick="flashFirmware()" title="Descarga e instala la ultima version del firmware en tu ESP32.">
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
                    <span data-i18n="install_firmware">Instalar Firmware</span>
                </button>
            </div>
'''
html = html.replace('</div>\n        </div>\n\n        <!-- CENTER PANEL: Visual Mockup -->', firmware_btn + '        </div>\n        </div>\n\n        <!-- CENTER PANEL: Visual Mockup -->')
codecs.open('templates/index.html', 'w', 'utf-8').write(html)


# Now fix static/app.js
os.system('git restore static/app.js')
js = codecs.open('static/app.js', 'r', 'utf-8').read()

flash_js = '''
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
js = js + flash_js
codecs.open('static/app.js', 'w', 'utf-8').write(js)
print("Reverted Custom Anim but kept Firmware button")
