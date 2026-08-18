import re
import codecs

js = codecs.open('static/app.js', 'r', 'utf-8').read()

pattern = r"if \(typeof toggleCustomAnim === 'function'\) toggleCustomAnim\(\);\s*\}"
if re.search(pattern, js):
    js = re.sub(pattern, "if (typeof toggleCustomAnim === 'function') toggleCustomAnim();", js)
    codecs.open('static/app.js', 'w', 'utf-8').write(js)
    print("Fixed syntax")
else:
    print("Not found")
