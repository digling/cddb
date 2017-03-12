from pycddb.dataset import Dataset
from lingpy import Wordlist, csv2list
from lingpy.compare.partial import _get_slices

def prepare(ds):
    errs = 0
    wl = Wordlist(ds.raw('bds.tsv'))
    W = {}
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
            
            clpa = ds.transform(ipa, 'CLPA')
            struc = ds.transform(ipa, 'Structure')
            try:
                assert len(clpa.split(' ')) == len(struc.split(' '))
            except:
                errs += 1
                print(errs, clpa, struc)
            if '«' in clpa:
                errs += 1
                print(errs, ipa, clpa, struc)
            W[k] = [doc, wl[k, 'concept'], wl[k, 'concepticon_id'], value,
                    clpa, struc, wl[k, 'partial_ids']]
    W[0] = ['doculect', 'concept', 'concepticon_id', 'value', 'segments', 'structure', 'cogids']
    ds.write_wordlist(Wordlist(W))

def inventories(ds):
    data = csv2list(ds.raw('inv.tsv'))
    header = data[0]
    invs = {l: [] for l in ds.languages}
    for i, line in enumerate(data[1:]):
        stype, sis, ipa, struc = line[1:5]
        if len(struc.split()) != len(ipa.split()):
            print(i+2, 'warn', struc, '  |  ', ipa)
        for l, n in zip(header[5:], line[5:]):
            if n:
                note = '' if 'X' else n
                invs[l] += [[sis, ipa, struc, stype, note]]
    ds.write_inventories(invs)


        


