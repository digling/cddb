from pycddb.dataset import Dataset
from lingpy import *
from lingpy import *
from glob import glob
import re
from collections import defaultdict
from pyconcepticon.api import Concepticon
from pyclpa.base import get_clpa
from pycddb.util import get_transformer
from sinopy import sinopy

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
            cddb = transform(value, 'CDDB').split(' ')
            src = transform(value, 'SOURCE').split(' ')
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

def _parse_chars(chars):
    plus = ''
    bracket = False
    out, notes, marks = [], [], []
    for c in chars:
        if bracket:
            if c in '>)':
                bracket = ''
            else:
                notes[-1] += c
        elif c not in '(<[':
            if c in '+-':
                plus = c
            else:
                if c in '～兒儿':
                    marks += [c]
                elif not plus and not bracket:
                    out += [c]
                    notes += ['']
                    marks += ['']
                elif plus:
                    out[-1] += c+plus
                    plus = ''
        else:
            bracket = c
    return list(zip(out, notes, marks))


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
                all_strucs = []
                all_vals = []
                for sampa in sampas:
                    #print(f.split('/')[-1], idx, concept, page, sampa)
                    if sampa.startswith('('):
                        sampa = sampa[sampa.index(' ')+1:]
                    morphemes = sampa.split(' ')
                    mymorphs = []
                    mysrcs = []
                    mystrucs = []
                    for morpheme in morphemes:
                        #print(f, concept, page, char, sampa, line)
                        morph = re.sub(r'([012345\-_]+)$', r'<\1>',
                                morpheme) 
                        #get all tone combis
                        tones = re.findall('<.*?>', morph)
                        for tone in tones:
                            newtone = ''.join([tone_converter.get(x, x) for x in tone])
                            morph = morph.replace(tone, newtone[1:-1])

                        ipa = transform(r''+morph, 'CDDB').replace(' ⁻ ', '⁻') 
                        src = transform(r''+morph, 'SOURCE').replace(' ⁻ ', '⁻') 
                        struc = transform(r''+morph, 'STRUCTURE').replace(' ⁻ ', '⁻')
                        if '?' in ipa:
                            print(f.split('/')[-1], page, morph, morpheme, ipa)
                            input()
                        mymorphs += [ipa]
                        mysrcs += [src]
                        mystrucs += [struc]
                    all_morphs += [' + '.join(mymorphs)]
                    all_strucs += [' + '.join(mystrucs)]
                    all_vals += [' '.join(list([v.replace(' ', '') for v in
                        mysrcs]))]
                blocks[-1] += [[idx, concept, page, sampas,
                    char.split(','),all_morphs, all_vals, all_strucs, f]]
                if idx == 19:
                    #print(len(blocks[-1]), blocks[-1])
                    assert len(blocks[-1]) == 19
                    idx = 0
    return blocks


def _get_plus(chars):
    last = ''
    out = []
    for i, char in enumerate(chars):
        if char in "+-":
            out += [char+chars[i-1]+chars[i+1]]
    return out

def prepare(ds):
    concepts = dict([(x.english, (x.concepticon_id, x.attributes['chinese']))
        for x in Concepticon().conceptlists['Liu-2007-201'].concepts.values()])
    blocks = _get_data(ds)
    D, idx = {}, 1
    id2lang = dict([(ds.languages[x][ds.id+'_id'], x) for x in
        ds.languages])
    errors = set()
    for block in blocks:
        for i, (_idx, concept, page, sampas, chars, words, vals, strucs, f) in enumerate(block):
            langid = str(i+1)
            lang = id2lang[langid]
            for j, morph in enumerate(words):
                cid, chinese = concepts.get(concept, ('?', '?'))
                if morph != '-':
                    if cid == '?':
                        errors.add(concept)
                    try:
                        D[idx] = [lang, langid, concept, chinese, cid, chars[j],
                                vals[j],
                                ' '.join(ipa2tokens(morph, semi_diacritics='sɕʑʃʂʐz', 
                                    expand_nasals=True, merge_vowels=False)),
                                
                                
                                strucs[j].replace('t / t',
                                        'T'),
                                sampas[j], page]
                        idx += 1
                    except:
                        print(chars, words, f)
                        raise
    D[0] = ['doculect', 'doculect_id', 'concept', 'concept_chinese',
            'concepticon_id', 'characters_is', 'value', 'segments', 'structure', 'sampa', 'page']
    wl = Wordlist(D)

    # correct characters
    count = 1
    problems = {}
    for k, chars, segments in iter_rows(wl, 'characters_is', 'segments'):
        charnotes = _parse_chars(chars)
        morphemes = segments.split(' + ')
        if len(charnotes) != len(morphemes):
            print(
                    [c[0] for c in charnotes],
                    [c[2] for c in charnotes],
                    segments, count, k, wl[k, 'doculect'], wl[k, 'concept'])
            count += 1
            problems[k] = '1'
        else:
            problems[k] = ''


    # get the errors for characters with a plus
    plussed = []
    for idx, chars in iter_rows(wl, 'characters_is'):
        plussed += _get_plus(chars)
    
    _t = {}
    for i,char in enumerate(sorted(set(plussed))):
        new_char = sinopy.character_from_structure(char)
        if len(new_char) == 1:
            _t[char] = new_char

    notes = {}
    #for k in problems:
    #    print(wl[k, 'doculect'], wl[k, 'characters'], wl[k, 'segments'])
    for k, chars in iter_rows(wl, 'characters_is'):
        charnotes = _parse_chars(chars)
        notes[k] = [
                ''.join([x[0] for x in charnotes]),
                ''.join([x[1] for x in charnotes]),
                ''.join([x[2] for x in charnotes]),
                ]
        if '+' in notes[k][0]:
            new_chars = []
            for char in charnotes:
                if '+' in char[0]:
                    test = sinopy.character_from_structure(
                            '+'+char[0][:2])
                    if test != '?':
                        new_chars += [test]
                    else:
                        new_chars += [char[0][:2]]
                else:
                    new_chars += [char[0]]

            notes[k][0] = sinopy.gbk2big5(' '.join(new_chars))
        else:
            notes[k][0] = ' '.join(list(notes[k][0]))

            

    wl.add_entries('characters', notes, lambda x: x[0])
    wl.add_entries('lexeme_note', notes, lambda x: x[1])
    wl.add_entries('character_note', notes, lambda x: x[2])

    partials = {}
    converter = {}
    idx = 1
    for k, chars, morphs in iter_rows(wl, 'characters', 'segments'):
        _ms, _cs = morphs.split(' + '), chars.split(' ')
        print(_cs)
        pidxs = []
        for char in _cs:
            if char in partials:
                pidx = partials[char]
            else:
                pidx = idx
                idx += 1
                partials[char] = pidx
            pidxs += [str(pidx)]
        if len(pidxs) < len(_ms):
            pidxs += ['0', '0', '0']
            pidxs = pidxs[:len(_ms)]
        
        converter[k] = ' '.join(pidxs)
    wl.add_entries('cogids', converter, lambda x: x)


    # retrieve structures
    strucs = defaultdict(int)
    for k, s in iter_rows(wl, 'structure'):
        for s_ in s.split(' + '):
            strucs[s_] += 1
    for s in sorted(strucs, key=lambda x: strucs[x]):
        print('{0:10}'.format(s), strucs[s])



    ds.write_wordlist(wl)
    print(errors, count)
        

    


