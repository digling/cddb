import re
from lingpy import *
from sinopy import sinopy

def get_brackets(string, b='()'):
    bropen = False
    out1 = ''
    out2 = ''
    chars = list(string)
    while chars:
        char = chars.pop(0)
        if char == b[0]:
            bropen = True
        if bropen:
            out2 += char
        else:
            out1 += char
        if char == b[1]:
            bropen = False
    return out1.strip(), out2.strip()

def prepare(ds):

    data = csv2list(ds.get_path('raw', 'D_ocbs.tsv'), strip_lines=False)
    header = data[0]
    out = [[
        'ID', 'CHARACTER', 'PINYIN', 'DOCULECT', 'VALUE', 'SEGMENTS',
        'CONTEXT', 'GLOSS',
        'KARLGREN_ID', 'RHYME_CLASS', 'PHONETIC_CLASS', 'COGNATE_CLASS'
        ]]
    idx = 1
    errors = set()
    for i, line in enumerate(data[1:]):
        
        
        char = line[0]
        mch = line[1]
        pinyin = line[2]
        och = ''.join([x for x in line[3] if x not in '[]'])

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
        
        # get mch and mch_structure
        msegments, mstructure = ds.mch(mch)
        out += [[idx, char, pinyin, 'Middle_Chinese', mch, msegments,
            mstructure, ds.gloss(gloss), kg, '', '', str(i+1)]]
        idx += 1
        if '«' in msegments:
            print('[MCH] : ', mch)
        
        csegments, cstructure = ds.och(och)
        if '«' in csegments:
            errors.add(och)

        out += [[idx, char, pinyin, 'Old_Chinese', line[3],
            csegments, cstructure, ds.gloss(gloss), kg, rhyme, kg[:4], str(i+1)]]
    idx += 1
    ds.write_characters(out)

