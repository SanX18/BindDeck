import re
import codecs

html = codecs.open('templates/index.html', 'r', 'utf-8').read()

target = r'<label for="customAnimFile" class="btn-secondary" style="display:\s*inline-block; width: 100%; text-align: center; cursor: pointer; font-size: 0.85rem; padding: 0.4rem;">.*?<p id="customAnimStatus" style="font-size: 0.75rem; color:\s*var\(--text-muted\); margin-top: 5px; text-align: center; margin-bottom: 0;"></p>'

replacement = '''<label for="customAnimFile" class="btn-secondary" style="display: inline-block; width: 100%; text-align: center; cursor: pointer; font-size: 0.85rem; padding: 0.4rem;">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="vertical-align: middle; margin-right: 5px;"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="12" y1="18" x2="12" y2="12"></line><line x1="9" y1="15" x2="15" y2="15"></line></svg>
                        Seleccionar Archivo .h
                    </label>
                    <input type="file" id="customAnimFile" accept=".h" style="display: none;" onchange="document.getElementById('customAnimName').innerText = this.files.length > 0 ? this.files[0].name : 'Ningun archivo seleccionado';">
                    <p id="customAnimName" style="font-size: 0.8rem; color: var(--text-main); margin-top: 5px; text-align: center;">Ningun archivo seleccionado</p>
                    <button type="button" class="btn-primary" style="width: 100%; padding: 0.5rem; margin-top: 5px;" onclick="uploadCustomAnim()">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="vertical-align: middle; margin-right: 5px;"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg>
                        Subir al Dispositivo
                    </button>
                    <p id="customAnimStatus" style="font-size: 0.75rem; color: var(--text-muted); margin-top: 5px; text-align: center; margin-bottom: 0;"></p>'''

if re.search(target, html, flags=re.DOTALL):
    html = re.sub(target, replacement, html, flags=re.DOTALL)
    codecs.open('templates/index.html', 'w', 'utf-8').write(html)
    print("UI fixed")
else:
    print("Target not found")
