import codecs
content = codecs.open('pc_monitor.py', 'r', 'utf-8').read()

patch = '''
# Monkeypatch subprocess.Popen para evitar ventanas CMD emergentes en Windows
import subprocess
import os

if os.name == 'nt':
    original_popen = subprocess.Popen
    class HiddenPopen(original_popen):
        def __init__(self, *args, **kwargs):
            if 'creationflags' not in kwargs:
                kwargs['creationflags'] = subprocess.CREATE_NO_WINDOW
            super().__init__(*args, **kwargs)
    subprocess.Popen = HiddenPopen
'''

if 'HiddenPopen' not in content:
    lines = content.split('\n')
    # find imports
    for i, line in enumerate(lines):
        if line.startswith('import subprocess'):
            lines.insert(i + 1, patch)
            break
    codecs.open('pc_monitor.py', 'w', 'utf-8').write('\n'.join(lines))
