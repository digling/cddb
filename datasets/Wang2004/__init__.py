from clldutils.dsv import UnicodeReader
from lingpy import Wordlist
from pyconcepticon.api import Concepticon
import os
from lingpy._plugins.chinese import sinopy

varieties_in_source = {"B": "Beijing",
		"Y": "Yingshan",
		"S": "Suzhou",
		"H": "Shanghai",
		"F": "Shuangfeng",
		"C": "Changsha",
		"N": "Nanchang",
		"G": "Guangzhou",
		"M": "Meixian",
		"X": "Xiamen"}


def prepare(dataset):
    concepts = dict(
            [(x.english, x.concepticon_id) for x in \
                    Concepticon().conceptlists['Wang-2004-100a'].concepts.values()]
                    )
    
    # correct wrong pinyins in sinopy
    pinyin = { "虱" : "shī", "咯" : "gē", "強" : "qiáng", "哩" : "lǐ", "喏" : "nuò", "鳧" : "fú", "伲" : "nǐ", "黃" : "huáng", "哋" : "dì", "阿" : "ā", "卵" : "luǎn", "說" : "shuō", "喙" : "huì", "頸" : "jǐng", "唔" : "wú}", "雞" : "jī", "黒" : "hēi", "哪" : "nǎ", "麼" : "me", "蔃" : "qiáng", "葷" : "hūn", "鳥" : "niǎo}", "舌" : "huà", "吃" : "chī", "膘" : "biǎo}", "綠" : "lǜ", "羽" : "yǔ", "們" : "men", "焦" : "jiāo", "腳" : "jiǎo", "乜" : "miē", "即" : "jí", "佬" : "lǎo", }

    with UnicodeReader(dataset.get_path(['raw', 'Wang2004.csv']), delimiter='\t') as reader:
        lines = list(reader)
    D = {}
    idx = 1
    cogids = {0 : 0}
    for line in lines[1:]:
        concept = line[0]
        cid = concepts[concept]
        for t, cogs in zip(lines[0][1:], line[1:]):
            taxon = varieties_in_source[t]
            for cog in cogs.split('/'):
                if cog in cogids:
                    cogid = cogids[cog]
                else:
                    cogid = max(list(cogids.values()) or 0) + 1
                    cogids[cog] = cogid
                D[idx] = [taxon, t, concept, cid, cog, cogid]
                idx += 1
    D[0] = ['doculect', 'doculect_in_source', 'concept', 'concepticon_id',
            'value', 'cogid']
    wl = Wordlist(D)
    
    # renumber for partial cognates
    pcogs, idx = {}, 1
    converter = {}
    for k in wl:
        chars = sinopy.gbk2big5(wl[k, 'value'])
        concept = wl[k, 'concept']
        cogids = []
        for char in chars:
            if sinopy.is_chinese(char):
                if char not in pcogs:
                    pcogs[char] = idx
                    idx += 1
                cchar = concept + ':' + str(pcogs[char])
                if cchar not in pcogs:
                    pcogs[cchar] = pcogs[char]
            else:
                cchar = concept + ':' + char
                if cchar not in pcogs:
                    pcogs[cchar] = idx
                    idx += 1
            cogids += [pcogs[cchar]]
        converter[k] = ' '.join([str(x) for x in cogids])
    wl.add_entries('cogids', converter, lambda x: x)
    wl.output('tsv', filename=dataset.get_path(['words']), prettify=False, ignore='all')
    
    # we also write the characters
    C = [['ID', 'CHARACTER', 'PINYIN', 'WORDS_COGIDS', 'WORDS_ID', 'CONCEPT', 'DOCULECT',
        'POSITION']]
    idx = 1
    errors = {}
    for k in wl:
        concept = wl[k, 'concept']
        doculect = wl[k, 'doculect']
        chars = sinopy.gbk2big5(wl[k, 'value'])
        cogids = wl[k, 'cogids'].split(' ')
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
    with open(dataset.get_path(['characters.csv']), 'w') as f:
        for line in C:
            f.write('\t'.join([str(x) for x in line])+'\n')
    
    # prepare the trees
    with open(dataset.get_path(['raw', 'tree-100.tre'])) as f1:
        with open(dataset.get_path(['trees', 'tree-100.tre']), 'w') as f2:
            f2.write(''.join([varieties_in_source.get(x, x) for x in f1.read()]))
    with open(dataset.get_path(['raw', 'tree-95.tre'])) as f1:
        with open(dataset.get_path(['trees', 'tree-95.tre']), 'w') as f2:
            f2.write(''.join([varieties_in_source.get(x, x) for x in f1.read()]))
