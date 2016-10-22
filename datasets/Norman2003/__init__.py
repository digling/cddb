from pycddb.dataset import Dataset
from pyconcepticon.api import Concepticon
from clldutils.dsv import UnicodeReader
from lingpy._plugins.chinese import sinopy
from lingpy import *

def prepare(dataset):

    concepts = dict([(x.english, (x.concepticon_id, x.attributes['chinese'])) for x in
        Concepticon().conceptlists['Norman-2003-40'].concepts.values()])
    id2lang = dict([(dataset.languages[x][dataset.id+'_id'], x) for x in
        dataset.languages])
    with UnicodeReader(dataset.get_path('raw', 'Norman2003a.tsv'),
            delimiter='\t') as reader:
        data = list(reader)
    header = data[0]
    D, idx = {}, 1
    for line in data[1:]:
        concept, number = line[1], line[0]
        cid, char = concepts[concept]
        for lidx, entry in zip(header[2:], line[2:]):
            lang = id2lang[lidx]
            source = dataset.languages[lang][dataset.id+'_source']
            D[idx] = [lang, lidx, concept, sinopy.gbk2big5(char), cid, entry, source]
            idx += 1
    D[0] = ['doculect', 'doculect_in_source', 'concept', 'concept_chinese',
        'concepticon_id', 'value', 'source']
    wl = Wordlist(D)
    wl.output('tsv', filename=dataset.get_path('words'), ignore='all',
            prettify=False)
    
    idx = 1
    with open(dataset.get_path('characters.tsv'), 'w') as f:
        f.write('\t'.join((
            'ID', 'WORDS_ID', 'POSITION', 'CHARACTER', 'PINYIN', 'GLOSS', 
            'DOCULECT', 'READING',
            'SOURCE'))+'\n')
        for k in wl.get_list(doculect='Common_Chinese', flat=True):
            f.write(str(idx)+'\t'+str(k)+'\t0\t'+'\t'.join([
                wl[k, 'concept_chinese'], sinopy.pinyin(wl[k,
                    'concept_chinese']), wl[k, 'concept'], 'Common_Chinese', wl[k, 'value'],
                wl[k, 'source']])+'\n')
            idx += 1

    with UnicodeReader(dataset.get_path('raw', 'Norman2003b.tsv'),
            delimiter='\t') as reader:
        data = list(reader)
    D = [('ID', 'STRUCTURE', 'STRUCTURE_ID', 'DOCULECT', 'DOCULECT_IN_SOURCE',
        'VALUE')]
    idx = 1
    header = data[0][2:]
    for line in data[1:]:
        number, category = line[:2]
        for lid, pap in zip(header, line[2:]):
            lang = dataset.lid2lang[lid]
            D += [(str(idx), category, number, lang, lid, pap)]
            idx += 1
    with open(dataset.get_path('structures.tsv'), 'w') as f:
        for line in D:
            f.write('\t'.join(line)+'\n')
