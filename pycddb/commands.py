from pycddb.util import *
from sinopy import sinopy
from pycddb.dataset import Dataset
from lingpy import *
from collections import defaultdict

def character_list():
    sources = get_sources('characters.tsv')
    master = defaultdict(list)
    
    doculects = set()
    for source in sources:
        print('[preparing]',source)
        ds = Dataset(source)
        for char in ds.characters.rows:
            tmp = ds.characters.get_dict(row=char)
            readings = []
            for t, chars in tmp.items():
                for c in chars:
                    if ds.characters[c, 'reading']:
                        readings += [(t, c, ds.characters[c, 'reading'])]
            for t, idx, r in readings:
                master[char].append((t, source, r, idx))
                doculects.add(t)
    
    table, idx = [], 1
    for i, (char, vals) in enumerate(master.items()):
        
        pinyin = sinopy.pinyin(char)
        if sinopy.is_chinese(pinyin) or '?' in pinyin or '!' in pinyin: pinyin = ''
        for t, s, r, cidx in vals:
            table += [(idx, char, pinyin, t, r, s, idx)]
            idx += 1
    with open(cddb_path('datasets', 'characters.tsv'), 'w') as f:
        f.write('ID\tCHARACTER\tDOCULECT\tSOURCE\tREADING\tCROSS_REF\n')
        for line in table:
            f.write('\t'.join([str(x) for x in line])+'\n')
