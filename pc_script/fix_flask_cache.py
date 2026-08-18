import codecs
py = codecs.open('pc_monitor.py', 'r', 'utf-8').read()

patch = '''
@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'
    return response
'''

if '@app.after_request' not in py:
    py = py.replace("if __name__ == '__main__':", patch + "\nif __name__ == '__main__':")
    codecs.open('pc_monitor.py', 'w', 'utf-8').write(py)
    print("Flask cache headers added")
