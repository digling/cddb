from pycddb.dataset import Dataset
from lingpy import *
from lingpy import *
from glob import glob
import re
from collections import defaultdict
from pyconcepticon.api import Concepticon
from pyclpa.base import get_clpa
from pycddb.util import get_transformer

def _prepare_inventories(dataset):
    clpa = get_clpa()
    files = glob(dataset.get_path('raw', 'inv-*.tsv'))
    dialects = []

    t = Tokenizer(dataset.get_path('raw', 'profile.prf'))
    sounds = defaultdict(lambda : defaultdict(set))
    transform = lambda x, y: unicodedata.normalize('NFC', t.transform(x, y))

    for f in files:
        data = csv2list(f)
        number, dialect = re.findall('inv-([0-9]+)-([a-z_A-Z]+)', 
                f)[0]
        for i, line in enumerate(data):
            print(dialect, number, i+1, ', '.join(line))
            page, sound, value, *rest = line
            if not rest: rest = ['']
            cddb = transform(value, 'cddb').split(' ')
            src = transform(value, 'source').split(' ')
            if len(src) != len(cddb):
                src = src + ['-', '-', '-']
            struct = t.transform(value, 'structure')
            for s1, s2, s3 in zip(cddb, struct, src):
                sounds[s1][s2].add((dialect, s3, rest[0]))
    table, idx = [('ID', 'SOUND', 'CLPA', 'POSITION', 'DOCULECT', 'SOUND_IN_SOURCE' )], 1
    for k, v in sorted(sounds.items(), key=lambda x: str(x[1])):
        c = clpa.segment2clpa(k)
        for s in sorted(v):
            for d, sr, r in sorted(v[s]):
                table += [(str(idx), k, c, s, d, sr)]
                idx += 1
    with open(dataset.get_path('inventories.tsv'), 'w') as f:
        for line in table:
            f.write('\t'.join(line)+'\n')

def _get_data(dataset):
    transform = get_transformer('Liu2007.prf')
    files = sorted(glob(dataset.get_path('raw', 'chinese-master.tsv')))
    concepts = defaultdict(set)
    tone_converter = dict(zip('012345-', '⁰¹²³⁴⁵⁻'))
    #tone_converter['_'] = ''
    D = {}
    D[0] = ['doculect', 'concept', 'benzi', 'ipa_in_source', 'page']
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
                    #print(f.split('/')[-1], idx, concept, page, sampa)
                    if sampa.startswith('('):
                        sampa = sampa[sampa.index(' ')+1:]
                    #try:
                    #    _t = transform(sampa, 'cddb').replace(' ⁻ ', '⁻')
                    #    print('\t', _t)
                    #except KeyError:
                    #    print(f.split('/')[-1], idx, concept, page, sampa)
                    #    input()
                    #all_morphs += [_t]
                    morphemes = sampa.split(' ')
                    mymorphs = []
                    for morpheme in morphemes:
                        #print(f, concept, page, char, sampa, line)
                        morph = re.sub(r'([012345\-_]+)$', r'<\1>',
                                morpheme) 
                        #get all tone combis
                        tones = re.findall('<.*?>', morph)
                        for tone in tones:
                            newtone = ''.join([tone_converter.get(x, x) for x in tone])
                            morph = morph.replace(tone, newtone[1:-1])

                        ipa = transform(r''+morph, 'cddb').replace(' ⁻ ', '⁻') 
                        if '?' in ipa:
                            print(f.split('/')[-1], page, morph, morpheme, ipa)
                            input()
                        mymorphs += [ipa]
                    all_morphs += [' + '.join(mymorphs)]
                blocks[-1] += [[idx, concept, page, sampas,
                    char.split(','),all_morphs, f]]
                if idx == 19:
                    #print(len(blocks[-1]), blocks[-1])
                    assert len(blocks[-1]) == 19
                    idx = 0
    return blocks

def prepare(ds):
    concepts = dict([(x.english, (x.concepticon_id, x.attributes['chinese']))
        for x in Concepticon().conceptlists['Liu-2007-201'].concepts.values()])
    blocks = _get_data(ds)
    D, idx = {}, 1
    id2lang = dict([(ds.languages[x][ds.id+'_id'], x) for x in
        ds.languages])
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
            'concepticon_id', 'characters', 'value', 'segments', 'sampa', 'page']
    wl = Wordlist(D)
    ds.write_wordlist(Wordlist(D))
    print(errors)


    


