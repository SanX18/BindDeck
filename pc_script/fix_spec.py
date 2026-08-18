import codecs

spec = codecs.open('MacroDeck_v4.spec', 'r', 'utf-8').read()
spec = spec.replace("name='MacroDeck_v4'", "name='MacroDeck_v5'")
codecs.open('MacroDeck_v5.spec', 'w', 'utf-8').write(spec)
