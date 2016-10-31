from lingpy import *
from collections import defaultdict
invs = csv2list('inventories.tsv', strip_lines=False)
segments = defaultdict(dict)
langs = set()
for d, t, v, a, n in invs[1:]:
    if a.strip():
        allophone, context = a.split('/')
        segments[allophone, t][d] = (v, context)
    segments[v, t][d] = (a, n or 'X')
    langs.add(d)
langs = sorted(langs)
with open('Allen2007.prf', 'w') as f:
    f.write('GRAPHEMES\tTYPE\tAllen2007\tCLPA\tSTRUCTURE\t'+'\t'.join(langs)+'\n')
    for a, b in sorted(segments):
        f.write('\t'.join([a, b, a, a, '']))
        for lang in langs:
            vals = segments[a, b].get(lang, ['', ''])
            if vals[0] and vals[1]:
                value = '/'.join(vals)
            else:
                value = ''.join(vals)
            f.write('\t'+value)
        f.write('\n')

