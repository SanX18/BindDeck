import codecs

html = codecs.open('templates/index.html', 'r', 'utf-8').read()
html = html.replace('app.js?v=25', 'app.js?v=26').replace('app.js?v=24', 'app.js?v=26')
codecs.open('templates/index.html', 'w', 'utf-8').write(html)
