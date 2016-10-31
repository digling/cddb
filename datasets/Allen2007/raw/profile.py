from lingpy import *
from lingpy.compare.partial import _get_slices

wl = Wordlist('bds.tsv')
segments = set()
for k in wl:
    tokens = wl[k, 'tokens']
    #print(k, ' '.join(tokens))
    #if '(' in tokens:
    #    print(k)
    #    input()
    if ''.join(tokens):
        slices = _get_slices(tokens)
        for a, b in slices:
            this = tokens[a:b]
            classes = tokens2class(this, 'cv')
            if classes[0].lower() == 'c':
                ini, final = tokens[a:b][0], tokens[a:b][1:]
                segments.update([(' '.join(ini), 'i'), (' '.join(final), 'f')])
            else:
                segments.add((' '.join(this), 'f'))
for seg in segments:
    print(''.join(seg[0].split(' ')), '\t', seg[1])

