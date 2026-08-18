import codecs

html = codecs.open('templates/index.html', 'r', 'utf-8').read()

# 1. Remove the old tutorial button from the left panel
old_btn = '''            <button class="btn-secondary" id="btn-tutorial" style="width: 100%; border-color: var(--primary); color: var(--primary); display: flex; justify-content: center; align-items: center; gap: 8px;" title="Ver un tutorial rápido sobre cómo usar la aplicación.">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"></path><line x1="12" y1="17" x2="12.01" y2="17"></line></svg>
                Ver Tutorial
            </button>'''
html = html.replace(old_btn + '\n', '')

# 2. Add the new tutorial button in the header, next to btn-open-about
header_btn = '''
            <button id="btn-tutorial-header" title="Ver tutorial" style="background:transparent; border:none; color:var(--text-main); cursor:pointer; display: flex; align-items: center; justify-content: center; opacity: 0.8; transition: opacity 0.2s;" onmouseover="this.style.opacity='1'" onmouseout="this.style.opacity='0.8'">
                <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"></path><line x1="12" y1="17" x2="12.01" y2="17"></line></svg>
            </button>'''
# Find the btn-open-about and insert right before it
html = html.replace('<button id="btn-open-about"', header_btn.lstrip() + '\n            <button id="btn-open-about"')

# Fix encoding issue in tutorial modal
html = html.replace('', '¡').replace('rǭpido', 'rápido')

codecs.open('templates/index.html', 'w', 'utf-8').write(html)
