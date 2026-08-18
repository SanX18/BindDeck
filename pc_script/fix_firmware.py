import re
import codecs

html = codecs.open('templates/index.html', 'r', 'utf-8').read()

button_html = '''            <div class="form-group" style="border-top: 1px solid var(--border); padding-top: 15px; margin-top: auto;">
                <button class="btn-secondary" style="width: 100%; display: flex; align-items: center; justify-content: center; gap: 10px;" id="btn-flash-firmware" onclick="flashFirmware()" title="Descarga e instala la ultima version del firmware en tu ESP32.">
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
                    <span data-i18n="install_firmware">Instalar Firmware</span>
                </button>
            </div>
'''

if 'btn-flash-firmware' not in html:
    # Find the closing tag of left-panel. It is right before "<!-- CENTER PANEL: Visual Mockup -->"
    # We'll use regex to inject it right before the last two </div> tags before CENTER PANEL
    pattern = r'(</div>\s*</div>\s*<!-- CENTER PANEL: Visual Mockup -->)'
    html = re.sub(pattern, button_html + r'\1', html)
    codecs.open('templates/index.html', 'w', 'utf-8').write(html)
    print("Firmware HTML injected")

