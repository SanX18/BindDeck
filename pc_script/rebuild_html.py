# -*- coding: utf-8 -*-
import codecs

html = codecs.open('templates/index.html', 'r', 'utf-8').read()

# 1. Add Firmware button back to left panel
firmware_btn = '''        <div style="margin-top: auto; padding-top: 15px; border-top: 1px solid var(--border); text-align: center;">
            <button class="btn-secondary" id="btn-flash-firmware" style="width: 100%; border-color: #ef4444; color: #ef4444; display: flex; justify-content: center; align-items: center; gap: 8px;" title="Borra y reinstala el firmware base en tu ESP32. Usa esto si el dispositivo deja de responder o la pantalla se queda en negro.">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="7 10 12 15 17 10"></polyline><line x1="12" y1="15" x2="12" y2="3"></line></svg>
                Instalar Firmware
            </button>
        </div>'''
html = html.replace('</div>\n        </div>\n\n        <!-- CENTER PANEL: Visual Mockup -->', firmware_btn + '\n        </div>\n        </div>\n\n        <!-- CENTER PANEL: Visual Mockup -->')

# 2. Add header button
header_btn = '''<button id="btn-tutorial-header" title="Ver tutorial" style="background:transparent; border:none; color:var(--text-main); cursor:pointer; display: flex; align-items: center; justify-content: center; opacity: 0.8; transition: opacity 0.2s;" onmouseover="this.style.opacity='1'" onmouseout="this.style.opacity='0.8'">
                <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"></path><line x1="12" y1="17" x2="12.01" y2="17"></line></svg>
            </button>\n            '''
html = html.replace('<button id="btn-open-about"', header_btn + '<button id="btn-open-about"')

# 3. Add modal to end
tutorial_html = '''
    <!-- Tutorial Modal -->
    <div id="tutorial-modal" class="modal" style="display: none;">
        <div class="modal-content" style="max-width: 500px; text-align: center;">
            <h2 id="tut-title" style="margin-bottom: 15px;">¡Bienvenido a MacroDeck!</h2>
            <p id="tut-text" style="color: var(--text-muted); margin-bottom: 20px; min-height: 60px;">
                Vamos a darte un rápido paseo para que descubras todo lo que puedes hacer con tu dispositivo.
            </p>
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span id="tut-progress" style="font-size: 12px; color: var(--text-muted);">1 / 4</span>
                <div>
                    <button id="tut-btn-skip" class="btn" style="background: transparent; color: var(--text-muted); border: 1px solid var(--border);">Omitir</button>
                    <button id="tut-btn-next" class="btn btn-primary">Siguiente</button>
                </div>
            </div>
        </div>
    </div>
'''
html = html.replace('</body>', tutorial_html + '\n</body>')

codecs.open('templates/index.html', 'w', 'utf-8').write(html)
