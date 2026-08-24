import codecs

spec = codecs.open('BindDeck_v4.spec', 'r', 'utf-8').read()
spec = spec.replace("name='BindDeck_v4'", "name='BindDeck_v5'")
codecs.open('BindDeck_v5.spec', 'w', 'utf-8').write(spec)
