import re
from lingpy import *
from sinopy import sinopy

def prepare(dataset):

    data = csv2list(dataset.get_path('raw', 'D_ocbs.tsv'), strip_lines=False)
    header = data[0]
    out = [[
        'ID', 'CHARACTER', 'PINYIN', 'DOCULECT', 'READING', 'SEGMENTS', 'GLOSS',
        'KARLGREN_ID', 'RHYME_CLASS', 'PHONETIC_CLASS', 'SOURCE'
        ]]
    for i, line in enumerate(data[1:]):
        
        char = line[0]
        mch = line[1]
        pinyin = line[2]
        och = line[3]
        pref = line[4].strip('-') or '-'
        ini = line[5] or '-'
        med = line[6] or '-'
        nuc = ' '.join(re.split('([Aaeiouə])', ''.join([x for x in line[7] if x
            not in '[]()'])))
        fin = line[8] or '-'
        segments = strip_chars('[]()', ' '.join([pref, ini, med, nuc, fin]))
        kg = line[9]
        gloss = line[11]
        rhyme = '-'+''.join([x for x in line[7] if x not in '[]()'])
        out += [[i+1, char, pinyin, 'Middle_Chinese', mch,
            ' '.join(sinopy.parse_chinese_morphemes(
                sinopy.baxter2ipa(mch))), gloss, kg, '', '', 'Baxter2014']]
        out += [[i+1, char, pinyin, 'Old_Chinese', och,
            segments, gloss, kg, rhyme, kg[:4], 'Baxter2014']]

    dataset.write_characters(out)

