from pycddb.dataset import Dataset
from lingpy import *
from lingpy.sequence.sound_classes import tokens2morphemes
from collections import defaultdict
from sinopy import sinopy as sp
import re
from pyconcepticon.api import Concepticon
from lingpy.compare.partial import Partial

def inventories(ds):

    data = csv2list(ds.raw('inventories.tsv'), strip_lines=False)
    invs = {l: [] for l in ds.languages}
    for i, line in enumerate(data):
        if len(line) == 4:
            src = line[2].replace(' ', '')
        else:
            src = line[4]
        if len(line[1].split()) != len(line[3].split()):
            print(i+1, 'warning', line[1], line[3], line[0])
        invs[line[0]] += [[src, line[3], line[1], '']]
    ds.write_inventories(invs)

def sandhi(string):
    down = '₀₁₂₃₄₅₆'
    up = '⁰¹²³⁴⁵⁶'
    idx = 0
    for i, s in enumerate(string):
        if s in down:
            new_string = string[i:] + '/' + string[:i]
            return ''.join([
                dict(zip(down, up)).get(x, x) for x in new_string])
    return string

def is_tone(string):
    nums = '⁰¹²³⁴⁵⁶'
    if [x for x in string if x in nums]:
        return True
    return False

def parse_chars(chars, language, tokens):

    numeric, plus = False, False
    out = []
    for char in chars:
        if char.isdigit() and char != '0' and not numeric:
            out += [char]
            numeric = True
        elif char.isdigit() and char != '0' and numeric:
            out[-1] += char
        elif char == '0':
            out += ['囗']
        elif char == '-':
            numeric = False
        elif char == '+':
            plus = True
        elif plus:
            out[-1] += char
            plus = False
        elif char in ['仔']:
            out += [char+'.'+language]
        else:
            out += [char]
    if out[0] == '':
        out = out[1:]
    if out[-1] == '兒' and len(out)-1 == len(tokens):
        out = out[:-1]

    return out

def prepare(ds):
    
    # steps:
    # parse characters (numbers, zeros)
    # check for number
    # recreate partial cognate identifiers
    # create strict cognate identifieres
    # code everything as CLDF-like file
    con = Concepticon()
    beida = con.conceptlists['BeijingDaxue-1964-905']
    inv = ds.sounds
    words = Wordlist(ds.raw('chars-corrected-2017-06-18.tsv'))
    partialids, pidc = {}, {}
    pidx = 1
    concepts = {}
    for idx, chars, tks, doculect, glossid in iter_rows(words, 'benzi', 'segments', 
            'doculect', 'beida_id'):
        tokens = tokens2morphemes(tks)
        benzi = parse_chars(chars, doculect, tokens)
        if len(tokens) != len(benzi):
            print(doculect, glossid, benzi, tokens)
        pids = []
        for char in benzi:
            if char == '囗':
                pids += [str(pidx)]
                pidx += 1
            else:
                if char not in partialids:
                    partialids[char] = str(pidx)
                    pidx += 1
                pids += [partialids[char]]
        words[idx, 'cogids'] = ' '.join(pids)
        words[idx, 'benzi'] = ' '.join(benzi)

        # retrieve correct concept 
        bidx = 'BeijingDaxue-1964-905-'+glossid
        concept = beida.concepts[bidx]
        concepts[idx] = [concept.concepticon_id, concept.attributes['chinese'],
                concept.attributes['pageno'], concept.attributes['pinyin']]
        words[idx, 'concept'] = concept.gloss + ' ('+concept.attributes['pinyin'] + ' '+concept.attributes['chinese']+')'
    for i, entry in enumerate(['concepticon_id', 'chinese', 'page', 'pinyin']):
        words.add_entries(entry, concepts, lambda x: x[i])
    words.add_entries('benzi_in_source', 'hanzi', lambda x: x)
    words.add_entries('source', 'ipa', lambda x: 'BeijingDaxue1964')
    words.add_entries('value', 'ipa', lambda x: x)
    words.add_entries('form', 'ipa', lambda x: x)
    words.add_entries('glottolog', 'doculect', lambda x:
        ds.languages[x]['glottolog'])
    words.add_entries('iso', 'doculect', lambda x: ds.languages[x]['iso'])

    # determine order of entries
    order = {}
    for d in words.cols:
        entries = words.get_list(col=d, flat=True)
        concept, oid = '', 1
        for idx in sorted(entries):
            new_concept = words[idx, 'concept']
            if new_concept == concept:
                oid += 1
            else:
                concept = new_concept
                oid = 1
            order[idx] = oid
    words.add_entries('order', order, lambda x: str(x))
    

    words.output('tsv', filename=ds.raw('tmp-2017-06-18'))
    print('first run on words')
    part = Partial(ds.raw('tmp-2017-06-18.tsv'), segments='segments')
    part.add_cognate_ids('cogids', 'cogid')
    part.output('tsv', filename=ds.raw('tmp-2017-06-18'))
    print('created cognate ids')
    alm = Alignments(ds.raw('tmp-2017-06-18.tsv'), segments='segments',
        ref='cogids', alignment='alignments')
    alm.align()
    alm.output('tsv', filename=ds.raw('tmp-2017-06-18-finalized'), subset=True, cols=[
        'doculect', 'glottolog', 'iso', 'concept', 'concepticon_id', 'chinese', 'pinyin', 'benzi', 'benzi_in_source',
        'value', 'form', 'segments', 'cogid', 'cogids', 'note', 'source', 'beida_id',
        'page', 'order', 'alignments'])
    words = Wordlist(ds.raw('tmp-2017-06-18-finalized.tsv'))
    ds.write_wordlist(words)
    with open('cldf/beijingdaxue1964.csv', 'w') as f:
        f.write(','.join(['ID', 'Language_name', 'Language_ID',
            'Language_iso', 'Parameter_ID', 'Parameter_name', 'Source',
            'Comment', 'Parameter_Chinese', 'Parameter_Pinyin', 'Value', 'Form',
            'Segments', 'Cognate_Set', 'Cognate_Sets', 'Alignments', 'Order',
            'Beida_ID', 'Page', 'Benzi', 'Benzi_in_source'])+'\n')
        for idx in words:
            out = [str(idx)]
            for entry in ['doculect', 'glottolog', 'iso', 'concepticon_id',
                'concept', 'source', 'note', 'chinese', 'pinyin', 'value', 'form',
                'segments', 'cogid', 'cogids', 'alignments', 'order', 'beida_id',
                'page', 'benzi', 'benzi_in_source']:
                value = words[idx, entry]
                if isinstance(value, list):
                    value = ' '.join([str(x) for x in value])
                else:
                    value = str(value)
                if '"' in value:
                    value = value.replace('"', '""')
                if ',' in value:
                    value = '"'+value+'"'
                out += [value]
            f.write(','.join(out)+'\n')



def prepare_old2(ds):
    
    converter = {
            '豬肉': '肉',
            '豬艤': '艤',
            '! □水': '口水',
            '! 一□水': '一口水',
            '星〔星兒〕': '星',
            "一串兒葡萄": "一串葡萄",
            "一小片兒草": "一小片草",
            "一串兒葡萄": "一串葡萄",
            "一抓兒葡萄": "一抓葡萄",
            "手套兒": "手套",
            "茄兒如": "茄如",
            "前兒日": "前日",
            "前兒個": "前個",
            "明兒個": "明個",
            "明兒個": "明個",
            "今兒個": "今個",
            "今兒日": "今日",
            "黃花兒魚": "黃花魚",
            "大前兒個": "大前個",
            "大前兒日": "大前日",
            "大後兒個": "大後個",
            
            }
    bad_list = []
    visited = []
    inv = ds.sounds
    words = Wordlist(ds.raw('words-2017-06-16.tsv'))
    weilist = []
    pids = {}
    pidx = 1
    characters, partialcogs = {}, {}
    blacklist = []
    for idx, bid, segments, chars, note in iter_rows(words, 'beida_id', 'segments',
            'hanzi', 'note'):
        if 'ignore' in note:
            blacklist += [idx] 
        else:
            ochars = chars
            chars = converter.get(chars, chars)
            chars = re.sub('〔[^〕]+〕', '', chars)
            chars = re.sub('<[^>]+>', '', chars)
            chars = chars.replace('□', '囗')
            chars = chars.replace('？', '')
            chars = ''.join([c for c in chars.split('，')[0] if sp.is_chinese(c)])
            tks = tokens2morphemes(segments)
            partials = []
            if len(tks) == len(chars):
                for char in chars:
                    if char in pids and char != '囗':
                        partials += [str(pids[char])]
                    else:
                        pids[char] = pidx
                        pidx += 1
                        partials += [str(pids[char])]
            else:
                if chars.endswith('兒'):
                    if len(chars)-1 == len(tks):
                        for char in chars[:-1]:
                            if char in pids and char != '囗':
                                partials += [str(pids[char])]
                            else:
                                pids[char] = pidx
                                pidx += 1
                                partials += [str(pids[char])]
                    else:
                        for tk in tks:
                            partials += [str(pidx)]
                            pidx += 1
                        bad_list += [idx]
                        print(len(bad_list), chars, len(tks), bid)
                elif not chars:
                    weilist += [idx]
                    for tk in tks:
                        partials += [str(pidx)]
                        pidx += 1
                    chars = '?' + chars
                elif '囗' in chars:
                    weilist += [idx]
                    for tk in tks:
                        partials += [str(pidx)]
                        pidx += 1
                    chars = '!' + chars
                else:
                    for tk in tks:
                        partials += [str(pidx)]
                        pidx += 1
                    bad_list += [idx]
                    print(len(bad_list), ochars, '|', '\t|', chars, len(tks), bid)
                    chars = ':' + chars
            characters[idx] = chars
            partialcogs[idx] = ' '.join(partials)
    print(len(weilist))
    words.output('tsv', filename=ds.raw('words.tmp'), subset=True,
            rows=dict(ID='not in '+str(blacklist)))
    words = Wordlist(ds.raw('words.tmp.tsv'))
    words.add_entries('benzi', characters, lambda x: x)
    words.add_entries('cogids', partialcogs, lambda x: x)
    ds.write_wordlist(words)

    

def prepare_old(ds):
    
    inv = ds.sounds
    ps = 0
    converter = {k: v for k, v in csv2list(ds.raw('converter.tsv'))}
    cleaner = [
            ('@ tɕ i a e ʔ ⁴', 'tɕ i æ ʔ ⁴'),
            ('l i a q ⁵⁵', 'l i a ŋ ⁵⁵'),
            ('ə r', '*/ə'), 
            ('a u r', '*/a u'), 
            ('ə n r', '*/ə n'), 
            ('a ŋ r', '*/a ŋ'), 
            ('ʅ r', '*/ʅ'), 
            ('i ŋ r', '*/i ŋ'), 
            ('a r', '*/a'),
            ('o r', '*/o'),
            ('u r', '*/u'),
            ('a n r', '*/a n'),
            ('u n r', '*/u n'),
            ('i n r', '*/i n'),
            ('i ŋ r', '*/i ŋ'),
            ('e r', '*/e'),
            ('e n r', '*/e n'),
            ('ə ŋ r', '*/ə ŋ'), 
            ('ə n r', '*/ə n'),
            ('y r', '*/y'),
            ('ɔ r', '*/ɔ'),
            ('a i r', '*/a i'),
            ('e i r', '*/e i'),
            ('i r', '*/i'),
            ('ɿ r', '*/ɿ'),
            ('ๅ r', '*/ɿ'),
            ('p fʰ', 'pfʰ'),
            ('ɛ r', '*/ɛ'),
            ('æ̃ ∼ r', '*/æ̃ ∼'),
            ('ẽ ∼ r', '*/ẽ ∼'),
            ('ĩ ∼ r', '*/ĩ ∼'),
            ('ə̃ ∼ r', '*/ə̃ ∼'),
            ('e ŋ r', '*/e ŋ'),
            ('ɑ r', '*/ɑ'), 
            ('ã ∼ r', '*/ã ∼'),
            ('æ r', '*/æ'),
            ('@ ', ''),
            ('@', ''),
            (' ❷', ''),
            ('& q u o t ;', '⁵¹'),

            ]
    D = {
            0: ['doculect', 'concept', 'hanzi', 'entry_in_source', 'beida_id',
                'ipa', 'tokens_old', 'segments', 'note']
    }
    iconv = {
            'Suzhou' : {
                'ɛ': 'ᴇ'},
            'Hefei': {
                'ɛ': 'ᴇ'},
            'Yangzhou': {
                'a': 'ɑ'}
            }
    for language in sorted(ds.languages):
        data = csv2list(ds.raw(language+'.tsv'), strip_lines=False)
        header = [h.lower() for h in data[0]]
        problems = defaultdict(int)
        for line in data[1:]:
            tmp = dict(zip(header, line))
            tks = tmp['tokens']
            for s, t in cleaner:
                tks = tks.replace(s, t)

            # first, check tokens against inventories
            out = []
            for tk in tks.split(' '):
                tk = converter.get(tk, tk)
                if is_tone(tk):
                    tk = sandhi(tk)

                if tk not in inv[language]:
                    if '/' in tk:
                        if tk.split('/')[1] not in inv[language]:
                            problems[tk] += 1
                            tk = '!!!'+tk
                    elif tk not in inv[language]:
                        if iconv.get(language, {}).get(tk):
                            tk = iconv.get(language)[tk]
                        else:
                            problems[tk] += 1
                            tk = '!!!'+tk
                out += [tk]
            D[int(tmp['id'])] = [tmp['doculect'], tmp['concept'], tmp['hanzi'],
                    tmp['entry_in_source'], tmp['beida_id'], tmp['ipa'],
                    tmp['tokens'], ' '.join(out), tmp['note']]
            if '<r>' in out:
                print(D[int(tmp['id'])])
        pps = 0
        for p, n in problems.items():
            if n > 5:
                print(language, '«', p, '»', n)
            ps += 1
            pps += n
        print('---')
        print(language, pps)
    print(ps)
    ds.write_wordlist(Wordlist(D))
        
