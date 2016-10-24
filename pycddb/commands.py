from pycddb.util import *
from sinopy import sinopy
from pycddb.dataset import Dataset
from lingpy import *
from collections import defaultdict

def character_list():
    sources = get_sources('characters.tsv')
    master = defaultdict(list)
    
    occs = defaultdict(list)
    doculects = set()
    for source in sources:
        print('[preparing]',source)
        ds = Dataset(source)
        for char in ds.characters.rows:
            occs[char] += [source]
            tmp = ds.characters.get_dict(row=char)
            readings = []
            for t, chars in tmp.items():
                for c in chars:
                    _data = (t, c, source, )
                    for h in ['reading', 'fanqie', 'phonetic_class', 
                            'semantic_class', 'rhyme_class',
                            'wordfamily_class', 'source']:
                        if ds.characters[c, h]:
                            _data += (ds.characters[c, h], )
                        else:
                            _data += ('', )

                    readings += [_data]
            for reading in readings:
                master[char].append(reading)
                doculects.add(t)
    
    table, idx = [], 1
    for i, (char, vals) in enumerate(master.items()):
        if len(occs[char]) == 2 and 'Guangyun' in occs[char] and 'Shuowen' in occs[char]:
            pass
        elif len(occs[char]) == 1 and ('Guangyun' in occs[char] or 'Shuowen' in
                occs[char]):
            pass
        else:
            pinyin = sinopy.pinyin(char)
            if sinopy.is_chinese(pinyin) or '?' in pinyin or '!' in pinyin: pinyin = ''
            for t, crossref, dataset, reading, fq, pc, sc, rc, wf, src in vals:
                table += [(idx, char, pinyin, t, reading, fq, pc, sc, rc, wf, src,
                    dataset, crossref)]
                idx += 1
    with open(cddb_path('datasets', 'characters.tsv'), 'w') as f:
        f.write('ID\tCHARACTER\tPINYIN\tDOCULECT\tREADING\tFANQIE\tPHONETIC_CLASS\tSEMANTIC_CLASS\tRHYME_CLASS\tWORDFAMILY_CLASS\tSOURCE\tDATASET\tDATASET_ID\n')
        for line in table:
            f.write('\t'.join([str(x) for x in line])+'\n')
