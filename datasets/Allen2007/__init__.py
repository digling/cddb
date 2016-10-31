from pycddb.dataset import Dataset
from lingpy import Wordlist, csv2list
from lingpy.compare.partial import _get_slices

def prepare(ds):
    errs = 0
    inv = csv2list(ds.raw('Allen2007.prf'), strip_lines=False)
    h = inv[0]
    I = {}
    for line in inv[1:]:
        tmp = dict(zip(h, line))
        I[tmp['CLPA']] = {k.lower(): v for k, v in tmp.items() if v.strip()}
    wl = Wordlist(ds.raw('bds.tsv'))
    for k in wl:
        value = wl[k, 'value']
        tokens = wl[k, 'tokens']
        doc = wl[k, 'doculect']
        if value:
            morphemes = []
            for a, b in _get_slices(wl[k, 'tokens']):
                ipa = ''.join(tokens[a:b])
                morphemes += [ipa]
            ipa = ' '.join(morphemes)
            
            clpa = ds.transform(ipa, 'clpa')
            struc = ds.transform(ipa, 'structure')
            try:
                assert len(clpa.split(' ')) == len(struc.split(' '))
            except:
                errs += 1
                print(errs, clpa, struc)

