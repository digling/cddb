from lingpy import *
import re

ST = {
        '\\' : 'c\\',
        "'" : '_h',
        '(' : '',
        ')' : '',
        '*' : '',
        '/' : '^-'
        }

def prepare(dataset):

    data = csv2list(dataset.get_path('raw', '__private__TSDict.csv'),
            strip_lines=False)
    header = data[0]
    out = {}
    idx = 1
    for line in data[1:]:
        i = int(line[0])
        chinese = line[1].replace(' ', '')
        concept = line[2].strip()
        trans = line[3].strip()
        sampa = re.sub(r'([0-5])', r'^\1', trans)
        for k, v in ST.items():
            sampa = sampa.replace(k, v)
        sampas = sampa.split('; ')
        try:
            words = []
            for sampa in sampas:
                if sampa:
                    ms = sampa.split(' ')
                    word = []
                    for m in ms:
                        if m:
                            ipa = sampa2uni(m)
                            tks = ' '.join(ipa2tokens(ipa, merge_vowels=False,
                                expand_nasals=True))
                            word += [tks]
                    if word:
                        words += [' + '.join(word)]
            for w in words:
                out[idx] = [i, 'Dancun', chinese, concept, trans, w, line[4]]
                idx += 1
        except:
            print('[ERROR]', i, sampas)
    out[0] = ['line_in_source', 'doculect', 'chinese', 'concept', 'value', 'segments',
            'characters']
    dataset.write_wordlist(Wordlist(out), 'words')
