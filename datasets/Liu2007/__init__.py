from pycddb.dataset import Dataset
from lingpy import *
from lingpy import *
from glob import glob
import re
from collections import defaultdict
from pyconcepticon.api import Concepticon

def _get_data(dataset):

    files = sorted(glob(dataset.get_path('raw', 'chinese-*.tsv')))
    tone_converter = dict(zip('012345-', '⁰¹²³⁴⁵¯'))
    tone_converter['_'] = ''
    converter = [
            ('E', 'ɛ'),
            ]
    concepts = defaultdict(set)
    D = {}
    D[0] = ['doculect', 'concept', 'hanzi_in_source', 'ipa_in_source', 'page']
    blocks = []
    cc = ''
    for f in files:
        data = csv2list(f)
        idx = 0
        for i, line in enumerate(data):
            if len(line) != 4:
                print(i, line)
                raise ValueError('wrong line number')
            concept, page, char, sampas = line
            if cc != concept:
                blocks += [[]]
            cc = concept
    
            concepts[concept].add(page)
            
            if sampas.startswith('!'):
                print(sampas)
                input()
            else:
                sampas = sampas.split(', ')
                idx += 1
                all_morphs = []
                for sampa in sampas:
                    if sampa.startswith('('):
                        sampa = sampa[sampa.index(' '):]
    
                    morphemes = sampa.split(' ')
                    mymorphs = []
                    for morpheme in morphemes:
                        #print(f, concept, page, char, sampa, line)
                        morph = re.sub(r'([012345\-_]+)$', r'<\1>',
                                morpheme) 
                        # get all tone combis
                        tones = re.findall('<.*?>', morph)
                        for tone in tones:
                            newtone = ''.join([tone_converter.get(x, x) for x in tone])
                            morph = morph.replace(tone, newtone[1:-1])
                        print(i, f.split('/')[-1], concept, page, sampas, morph)
                        ipa = sampa2uni(morph)
                        print('\t',morph, ipa)
                        mymorphs += [ipa]
                    all_morphs += ['+'.join(mymorphs)]
                blocks[-1] += [[idx, concept, page, sampas,
                    char.split(','),all_morphs, f]]
                if idx == 19:
                    #print(len(blocks[-1]), blocks[-1])
                    assert len(blocks[-1]) == 19
                    idx = 0
    return blocks

def prepare(dataset):
    concepts = dict([(x.english, (x.concepticon_id, x.attributes['chinese']))
        for x in Concepticon().conceptlists['Liu-2007-201'].concepts.values()])
    blocks = _get_data(dataset)
    D, idx = {}, 1
    id2lang = dict([(dataset.languages[x][dataset.id+'_id'], x) for x in
        dataset.languages])
    errors = set()
    for block in blocks:
        for i, (_idx, concept, page, sampas, chars, words, f) in enumerate(block):
            langid = str(i+1)
            lang = id2lang[langid]
            for j, morph in enumerate(words):
                cid, chinese = concepts.get(concept, ('?', '?'))
                if cid == '?':
                    errors.add(concept)
                try:
                    D[idx] = [lang, langid, concept, chinese, cid, chars[j], morph,
                            ' '.join(ipa2tokens(morph, semi_diacritics='sɕʑʃʂʐz', 
                                expand_nasals=True, merge_vowels=False)),
                            sampas[j], page]
                    idx += 1
                except:
                    print(chars, words, f)
                    raise
    D[0] = ['doculect', 'doculect_id', 'concept', 'concept_chinese',
            'concepticon_id', 'characters', 'value', 'tokens', 'sampa', 'page']
    wl = Wordlist(D)
    wl.output('tsv', filename=dataset.get_path('words'), ignore='all',
            prettify=False)
    print(errors)


    


