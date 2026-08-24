import re
with open('src/main.cpp', 'r', encoding='utf-8') as f:
    content = f.read()
content = re.sub(r'\s*potTrackMin = 32767;\n', '', content)
content = re.sub(r'\s*potTrackMax = 0;\n', '', content)
with open('src/main.cpp', 'w', encoding='utf-8') as f:
    f.write(content)
print("Fixed.")
