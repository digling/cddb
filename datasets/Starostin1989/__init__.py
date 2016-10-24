from urllib import request
from urllib import parse
import urllib
from pycddb.util import *
import json
import re
import lingpy

URL ="http://starling.rinet.ru/cgi-bin/response.cgi?root=config&morpho=0&basename=\data\china\\bigchina&first=1&off=&text_character="
FIELDS = {'Preclassic Old Chinese' : "Preclassic_Old_Chinese", 
        'Modern .Beijing. reading' : "pinyin",
        'Classic Old Chinese' : "Old_Chinese",
        'Western Han Chinese' : "Early_Han_Chinese",
        'Eastern Han Chinese' : "Late_Han_Chinese",
        'Early Postclassic Chinese' : 'epc',
        'Middle Postclassic Chinese' : 'mpc',
        'Late Postclassic Chinese' : 'lpc',
        'Middle Chinese' : "Middle_Chinese",
        'English meaning' : "gloss",
        'Russian meaning.s.' : "rgloss",
        'Comments' : "note",
        'Radical' : "semantic_class",
        'Four-angle index' : "fai",
        'Karlgren code': "karlgren_id",
        'Go-on' : "goon",
        'Kan-on' : "kanon",
        'Japanese reading' : "Japanese",
        'Vietnamese reading' : "Vietnamese",
        'Jianchuan Bai' : "Jianchuan",
        'Dali Bai' : "Dali",
        'Bijiang Bai' : "Bijiang",
        'Shijing occurrences' : "shijing_occ"
        }
LINKS = {'Sino-Tibetan etymology' : "st_link", 'Dialectal data': "dialects"}
HEADER = sorted([h for h in FIELDS] + [h for h in LINKS])

def download(dataset):
    print(HEADER)
    chars = load_characters()
    charset = []
    for k in chars:
        if chars[k, 'source'] == 'Baxter1992' or chars[k, 'source'] == 'Baxter2014':
            charset += [chars[k, 'character']]
    print('[Loaded Characters]') 
    for char in charset:
        _tmp = [x[0] for x in lingpy.csv2list(dataset.get_path('raw',
            'data-starostin.tsv'), strip_lines=True) if x]
        if not _tmp:
            out = open(dataset.get_path('raw', 'data-starostin.tsv'), 'w')
            out.write('CHARACTER'+'\t'+'\t'.join(HEADER)+'\n')
            out.close()
        _tmp += [x[0] for x in lingpy.csv2list(dataset.get_path('raw', 'data-missing.tsv'))]
        if char not in _tmp:
            new_url = URL + parse.quote(char)
            print('[LOADING] '+char+' '+new_url)
            try:
                req = request.urlopen(new_url)
                data = req.read().decode('utf-8')
                found = False
                tmp = {}
                for f in FIELDS:
                    d = re.findall(
                            '<span class="fld">'+f+':</span>.*?<span class="unicode">(.*?)</span>', 
                            data,
                            re.DOTALL
                            )
                    print(f, d)
                    if d:
                        tmp[f] = d[0]
                        found = True
                    else: tmp[f] = ''
                for l in LINKS:
                    d = re.findall(
                            '<span class="fld">'+l+':</span>.*?<a href="(.*?)"',
                            data,
                            re.DOTALL
                            )
                    print(l, d)
                    if d: tmp[l] = d[0]
                    else: tmp[l] = ''
                
                if found:
                    print('Found character {0} reading: {1}'.format(char,
                        tmp['Modern .Beijing. reading']))
                    out = open(dataset.get_path('raw', 'data-starostin.tsv'), 'a')
                    out.write(char+'\t'+'\t'.join([tmp[h].strip().replace('\t', '') for
                        h in HEADER])+'\n')
                    out.close()
                else:
                    print('Problem, ', len(data))
                    out = open(dataset.get_path('raw', 'data-missing.tsv'),
                            'a')
                    out.write(char+'\n')
                    out.close()
            except urllib.error.HTTPError:
                print('[ERROR IN LOADING URL]')


def prepare(dataset):

    data = lingpy.csv2list(dataset.get_path('raw', 'data-starostin.tsv'),
            strip_lines=False)
    header = [h.lower() for h in data[0]]
    out = {}
    idx = 1
    for line in data[1:]:
        char = line[0]
        coc = line[2]
        bijiang = line[1]
        note = line[3]
        dali = line[4]
        doc_url = line[5]
        lhc = line[7]
        gloss = line[8]
        jianchuan = line[12]
        kg = line[14]
        mch = line[16]
        pinyin = line[18]
        rad = line[20]
        shijing = line[21]
        
        if coc.strip():
            out[idx] = [char, pinyin, 'Old_Chinese', 'Classical Old Chinese', coc, rad,
                    kg[:4], kg, gloss]
            idx += 1
        if lhc.strip():
            out[idx] = [char, pinyin, 'Late_Han_Chinese', 'Eastern Han Chinese',
                    lhc,
                    rad,
                    kg[:4], kg, gloss]
            idx += 1
        if mch.strip():
            out[idx] = [char, pinyin, 'Middle_Chinese', 'Middle Chinese',
                    mch,
                    rad,
                    kg[:4], kg, gloss]
            idx += 1
    out[0] = ['character', 'pinyin', 'doculect', 'doculect_in_source', 'reading', 'semantic_class','phonetic_class', 'karlgren_id', 'gloss']
    dataset.write_wordlist(lingpy.Wordlist(out, row='character'), 'characters')

