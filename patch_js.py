with open('pc_script/static/app.js', 'r', encoding='utf-8') as f:
    js = f.read()

js = js.replace("const swNumber = e.target.innerText.split(' ')[1];", "const swNumber = e.target.innerText.includes('SW') ? e.target.innerText.split(' ')[1] : 'Encoder';")

with open('pc_script/static/app.js', 'w', encoding='utf-8') as f:
    f.write(js)
print("JS patched")
