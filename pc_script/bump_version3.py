import codecs
import re

html = codecs.open('templates/index.html', 'r', 'utf-8').read()
html = re.sub(r'app\.js\?v=\d+', 'app.js?v=27', html)
codecs.open('templates/index.html', 'w', 'utf-8').write(html)
