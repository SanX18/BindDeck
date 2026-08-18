import codecs

py = codecs.open('pc_monitor.py', 'r', 'utf-8').read()

cache_fix = '''
@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'
    return response

@app.route('/')
'''

if '@app.after_request' not in py:
    py = py.replace('@app.route(\'/\')', cache_fix)
    codecs.open('pc_monitor.py', 'w', 'utf-8').write(py)
    print("Cache fix added")
