import codecs
js = codecs.open('static/app.js', 'r', 'utf-8').read()
js = js.replace("document.getElementById('btn-tutorial')", "document.getElementById('btn-tutorial-header')")
codecs.open('static/app.js', 'w', 'utf-8').write(js)
