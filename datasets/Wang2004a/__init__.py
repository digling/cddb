from pycddb.util import renumber_partial
from lingpy import *
from sinopy import sinopy
from pyconcepticon.api import Concepticon

def prepare(dataset):

    # correct wrong pinyins in sinopy
    pinyin = { "虱" : "shī", "咯" : "gē", "強" : "qiáng", "哩" : "lǐ", "喏" : "nuò", "鳧" : "fú", "伲" : "nǐ", "黃" : "huáng", "哋" : "dì", "阿" : "ā", "卵" : "luǎn", "說" : "shuō", "喙" : "huì", "頸" : "jǐng", "唔" : "wú}", "雞" : "jī", "黒" : "hēi", "哪" : "nǎ", "麼" : "me", "蔃" : "qiáng", "葷" : "hūn", "鳥" : "niǎo}", "舌" : "huà", "吃" : "chī", "膘" : "biǎo}", "綠" : "lǜ", "羽" : "yǔ", "們" : "men", "焦" : "jiāo", "腳" : "jiǎo", "乜" : "miē", "即" : "jí", "佬" : "lǎo"}

    wl = Wordlist(dataset.get_path(['raw', 'D_wang-2006.tsv']))
    concepts = dict([(x.english, x.concepticon_id) for x in Concepticon().conceptlists['Wang-2006-200'].concepts.values()])
    D = {}
    och = csv2list(dataset.get_path(['raw', 'D_old_chinese.csv']))
    nidx = max([k for k in wl]) + 1
    
    wl.add_entries('concepticon_id', 'concept', lambda x: concepts[x])
    wl.add_entries('doculect_in_source', 'doculect', lambda x: x)
    
    for k in wl:
        doculect = wl[k, 'doculect'].replace('_B', '')
        D[k] = [wl[k, h] for h in ['doculect', 'doculect_in_source', 
            'concept', 'concepticon_id', 'ipa', 'partial']]
    
    D[0] = ['doculect', 'doculect_in_source', 
            'concept', 'concepticon_id', 'value', 'characters']
    for a, chars in och:
        for char in chars.split(','):
            if char != '-':
                D[nidx] = ['Old_Chinese', 'Old_Chinese', a, concepts[a], char,
                        char]
                nidx += 1

    wl2 = Wordlist(D)
    renumber_partial(wl2, name='cogids', partial_cognates='characters')
    wl2.output('tsv', filename=dataset.get_path(['words']), ignore='all',
            prettify=False)

    # we also write the characters
    C = [['ID', 'CHARACTER', 'PINYIN', 'WORDS_COGIDS', 'WORDS_ID', 'CONCEPT', 'DOCULECT',
        'POSITION']]
    idx = 1
    errors = {}
    for k in wl2:
        concept = wl2[k, 'concept']
        doculect = wl2[k, 'doculect']
        chars = sinopy.gbk2big5(wl2[k, 'value'])
        cogids = wl2[k, 'cogids'].split(' ')
        for i, (char, cogid) in enumerate(zip(chars, cogids)):
            if sinopy.is_chinese(char):
                py = sinopy.pinyin(char)
                py = pinyin.get(char, py)
                if '?' in py or '{' in py:
                    if char in errors:
                        pass
                    else:
                        errors[char] = py
                C += [[idx, char, py, cogid, k, concept, doculect, i]]
                idx += 1
    for k, v in errors.items():
        print('"'+k+'" : "'+v+'",')
    with open(dataset.get_path(['characters.tsv']), 'w') as f:
        for line in C:
            f.write('\t'.join([str(x) for x in line])+'\n')

