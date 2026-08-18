import codecs

html = codecs.open('templates/index.html', 'r', 'utf-8').read()
html = html.replace('class="modal"', 'class="modal-overlay"')
codecs.open('templates/index.html', 'w', 'utf-8').write(html)
