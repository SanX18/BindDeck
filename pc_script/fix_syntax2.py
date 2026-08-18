import codecs

js = codecs.open('static/app.js', 'r', 'utf-8').read()
js = js.replace('\<', '<')
js = js.replace('</div>\>', '</div>')
codecs.open('static/app.js', 'w', 'utf-8').write(js)
