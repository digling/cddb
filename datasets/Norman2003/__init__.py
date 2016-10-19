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
    with UnicodeReader(dataset.get_path(['raw', 'Norman2003a.tsv']),
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
    D[0] = ['doculect', 'doculect_in_source', 'concept', 'character',
        'concepticon_id', 'value', 'source']
    wl = Wordlist(D)
    wl.output('tsv', filename=dataset.get_path(['words']), ignore='all',
            prettify=False)
    

