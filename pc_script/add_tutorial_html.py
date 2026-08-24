# -*- coding: utf-8 -*-
import codecs

html = codecs.open('templates/index.html', 'r', 'utf-8').read()

tutorial_html = '''
    <!-- Tutorial Modal -->
    <div id="tutorial-modal" class="modal" style="display: none;">
        <div class="modal-content" style="max-width: 500px; text-align: center;">
            <h2 id="tut-title" style="margin-bottom: 15px;">¡Bienvenido a BindDeck!</h2>
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
