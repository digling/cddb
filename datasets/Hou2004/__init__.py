from pycddb.dataset import Dataset
from pycddb.util import slice_characters, slice_word
from sinopy import sinopy
from collections import defaultdict
from lingpy import *
from lingpy.convert.strings import write_nexus
from lingpy.sequence.sound_classes import syllabify
import re

rhymebook = sinopy._cd.GY
rhymebook['yun']['譚'] = 'om'
rhymebook['yun']['祃'] = rhymebook['yun']['禡']
rhymebook['yun']['狝'] = rhymebook['yun']['獮']
rhymebook['yun']['麇'] = rhymebook['yun']['真']
rhymebook['yun']['襇'] = rhymebook['yun']['襉']
rhymebook['yun']['恩'] = rhymebook['yun']['痕']
rhymebook['yun']['殷'] = rhymebook['yun']['真']
rhymebook['yun']['誌'] = rhymebook['yun']['志']
rhymebook['yun']['槨'] = rhymebook['yun']['鐸']
rhymebook['yun']['鹹'] = rhymebook['yun']['咸']
rhymebook['yun']['闞'] = rhymebook['yun']['蒸']
rhymebook['yun']['稱'] = rhymebook['yun']['蒸']

def check(dataset):

    wl = Wordlist(dataset.get_path(['raw', 'Hou2004-characters.tsv']))
    tmp = defaultdict(set)
    for k in wl:
        
        tmp[wl[k, 'gloss'], wl[k, 'baxter']].add(wl[k, 'zgyy'])
    
    errors = []
    count = 1
    for (g, k), vals in tmp.items():
        for v in vals:
            try:
                zgyy = sinopy.sixtuple2baxter(v, rhymebook=rhymebook)
            except ValueError:
                print(sinopy.sixtuple2baxter(v, debug=True, rhymebook=rhymebook))
                input()
                errors += [(v, k)]
                zgyy = None
            if zgyy:
                ipa = ''.join(zgyy).replace('P', '').replace('R','')
                if ipa != k:
                    print(count, g, k, ipa)
                    count += 1
    count = 1
    for a, b in errors:
        print(count, a, b)
        count += 1

def _prepare(ds):
    
    make_proto = lambda x: x.replace('←儿', '').replace('+儿', '')
    wl = Wordlist(ds.raw('Hou2004-lexemes(5).csv'))
    errc = 0
    D = {0 : ['doculect', 'concept', 'value', 'segments', 'structure',
        'benzi', 'characters', 'cognate_set', 'cognate_sets']}
    for k, d, c, i, h in iter_rows(wl, 'doculect', 'concept', 'ipa', 'counterpart'):
        ipa = re.sub('([⁰¹²³⁻⁴⁵]+)', r'\1 ', i).strip(' ')
        morphemes = ipa.split(' ')
        for j, m in enumerate(morphemes):
            if not m[-1] in '⁰¹²³⁴⁻⁵':
                morphemes[j] += '⁰'
        ipa = ' '.join(morphemes)
        tokens = ds.transform(ipa, 'clpa')
        struc = ds.transform(ipa, 'structure')
        proto = make_proto(h)

        if len(tokens.split(' + ')) != len(struc.split('+')):
            errc += 1
            print(errc, '\t', d, '\t', c, '\t', i, '\t', tokens, '\t',
                    struc)
        if '«' in struc:
            errc += 1
            print(errc, '\t', k, '\t', d, '\t', c, '\t', i, '\t', tokens, '\t',
                    struc)
        D[k] = [d, c, i, tokens, struc, h, proto, '0', '0']
    csets, cset = {}, {}
    cs1, cs2 = 1, 1
    structs = defaultdict(int)
    for k, d, c, i, h in iter_rows(wl, 'doculect', 'concept', 'ipa', 'counterpart'):
        chars = slice_characters(h.replace('←', ''))
        csl = len(chars)
        struc = D[k][4]
        if csl != len(struc.split('+')):
            errc += 1
            print(errc, '\t', k, '\t', d, '\t', c, '\t', i, '\t', h, '\t', struc)
        for s in struc.split(' + '):
            structs[s] += 1

        proto = make_proto(h)
        if proto in cset:
            pass
        else:
            cset[proto] = cs1
            cs1 += 1
        pids = []
        for p in proto:
            if p not in csets:
                csets[p] = cs2
                cs2 += 1
            pids += [str(csets[p])]
        D[k][-1] = ' '.join(pids)
    for k in wl:
        D[k][-2] = cset[D[k][-3]]
    
    ds.write_wordlist(Wordlist(D), 'raw/Hou-2004-180-lexemes')
    for s in sorted(structs, key=lambda x: structs[x]):
        print(s, structs[s])

def prepare(ds):
    
    convert = {k : v for k, v in [
                    ('ʻ','ʻ'),
                    ('‘','‘'),
                    ('‘','‘'),
                    ("'",'‘'),
                    ('"', '""'),
                    ('〜','~'),
                    ('A','ᴀ'),
                    ('□','口'),
                    ('口','口'),
                    ('Ã','ᴀ̃'),
                    ('E','ᴇ'),
                    ('Ẽ','ᴇ̃'),
                    ('ʔd','ʔd'),
                    ('ʔt','ʔt'),
                    ('ʔp','ʔp'),
                    ('ʔb','ʔb'),
                    ('ʔg','ʔg'),
                    ('ʔk','ʔk'),
                    ('I','ɪ'),
                    ('Ɣ','ɣ')]
            }

    translate = {'中古音韵' : '中古汉语'}
    data = csv2list(ds.raw('Hou-2004-characters.corrected.tsv'))
    headers = csv2list(ds.raw('headers.txt'))
    chin2cddb = {x['hanzi']: y for y, x in ds.languages.items()}
    header = {}
    for line in headers:
        idx, chars = line[0].split(' ')
        lng, srt = ds.gbk_and_big5(chars)
        char = lng[0]
        pinyin = ds.pinyin(char)
        header[line[0][1:-1]] = [char, lng, srt, pinyin]
    D = {
            0: [
                'doculect', 'character', 'pinyin', 'value', 'segments',
                'structure', 'cognate_class']}
    idx = 1
    prf = defaultdict(lambda : defaultdict(int))
    for line in data:
        if len(line) == 3:
            a, b, c = line
            d = []
        elif len(line) == 4:
            a, b, c, d = line
        else:
            a = False
        if a:
            doculect = chin2cddb[translate.get(a, a)]
            cogid = b[1:-1]
            txt = ''.join([convert.get(x, x) for x in c if
                x not in '\t \n\r"' and not sinopy.is_chinese(x)])
            if doculect != 'Middle_Chinese':
                for r in slice_word(ipa2tokens(txt, merge_vowels=False,
                    semi_diacritics="ɕ‘'ʑsz'ʂʐʃʒf", expand_nasals=True)):
                    if '~' in r:
                        pass
                    else:
                        tks = ''.join(r) 
                        i, f, t = ds.split_initial_final(tks)
                        if f and t:
                            if i:
                                prf[i, 'i'][doculect] += 1
                            prf[f, 'f'][doculect] += 1
                            prf[t, 't'][doculect] += 1
                        elif f:
                            if i: prf[i, 'i'][doculect] += 1
                            prf[f, 'f'][doculect] += 1
                        else:
                            prf[i+f+t, 's'][doculect] += 1
    ds.write_profile(ds.raw('hou-characters.prf'), prf)


def nexus(ds): 
    commands=['set autoclose=yes nowarn=yes;', 
            'lset coding=noabsencesites rates=gamma;', 'constraint root=1-.;',
            'prset brlenspr=clock:uniform;', 
            'prset clockvarpr=igr igrvarpr=exp(200);', 
            'prset sampleprob=0.2 samplestrat=random;',
            'prset speciationpr=exp(1);',
            'prset extinctionpr=beta(1,1);',
            'mcmcp ngen=2000000 printfreq=10000 samplefreq=2000 nruns=2' 
            ' nchains=4 savebrlens=yes filename=chinese-hou;', 
            'mcmc;', 'sumt;',
            'sump;'               
            ]
    wl = Wordlist(ds.raw('Hou-2004-180-lexemes.tsv'))
    chars = defaultdict(lambda : defaultdict(int))
    for k, d, cid, css in iter_rows(wl, 'doculect', 'cognate_sets', 'characters'):
        for c1, c2 in zip(cid.split(' '), css):
            chars[c1+':'+c2][d] += 1
    all_chars = sorted(chars, key=lambda x: sum(chars[x].values()))
    matrix = []
    for t in wl.taxa:
        matrix += [[]]
        for char in all_chars:
            if t in chars[char]:
                matrix[-1] += ['1']
            else:
                matrix[-1] += ['0']
    write_nexus(
            [t.replace("'", '_') for t in wl.taxa], 
            matrix,
            commands=commands,
            filename=ds.raw('chinese-hou.nex')
            )
    
    commands=['set autoclose=yes nowarn=yes;', 
            'lset coding=noabsencesites rates=gamma;', 'constraint root=1-.;',
            'prset brlenspr=clock:uniform;', 
            'prset clockvarpr=igr igrvarpr=exp(200);', 
            'prset sampleprob=0.2 samplestrat=random;',
            'prset speciationpr=exp(1);',
            'prset extinctionpr=beta(1,1);',
            'mcmcp ngen=2000000 printfreq=10000 samplefreq=2000 nruns=2' 
            ' nchains=4 savebrlens=yes filename=chinese-hou-lex;', 
            'mcmc;', 'sumt;',
            'sump;'               
            ]
    paps = wl.get_paps(ref='characters', entry='concept', missing='?')
    matrix = []
    for i, t in enumerate(wl.taxa):
        matrix += [[]]
        for p in paps:
            matrix[-1] += [str(paps[p][i])]
    write_nexus(
            [t.replace("'", '_') for t in wl.taxa], 
            matrix,
            commands=commands,
            filename=ds.raw('chinese-hou-lstat.nex')
            )


    
